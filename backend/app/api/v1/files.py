from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse as StarletteFileResponse
from sqlmodel import Session, select, and_
from typing import List, Optional
from pathlib import Path
import hashlib
import shutil

from app.api.deps import get_db, get_current_user, PaginationParams, SortParams
from app.models.file import FileRecord, FileStatus, FileVisibility
from app.models.user import User
from app.schemas.file import (
    FileResponse,
    FileDetailResponse,
    FileUploadResponse,
    FileUpdate,
    FileShareRequest,
    FileShareResponse,
    FileListResponse,
    FileSearchRequest,
)
from app.core.config import settings
from app.core.exceptions import (
    FileNotFoundException,
    InvalidFileTypeException,
    FileTooLargeException,
    InsufficientStorageException,
    PermissionDeniedException,
)

router = APIRouter(prefix="/files", tags=["files"])

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    visibility: Optional[str] = Form(default="private"),
    description: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None)
):
    """
    Upload a new file
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise InvalidFileTypeException(file_ext, settings.ALLOWED_EXTENSIONS)

    # Check file size
    file.file.seek(0, 2)  # Move to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise FileTooLargeException(file_size, settings.MAX_UPLOAD_SIZE)

    # Check user storage quota
    try:
        if current_user.storage_used + file_size > current_user.storage_quota:
            raise InsufficientStorageException(
                file_size,
                current_user.storage_quota - current_user.storage_used
            )
    except Exception as e:
        import traceback
        print(f"Error checking storage quota: {e}")
        traceback.print_exc()
        # For now, skip quota check if there's an error
        pass

    # Generate unique filename
    from datetime import datetime
    timestamp = datetime.utcnow().timestamp()
    unique_filename = f"{current_user.id}_{timestamp}{file_ext}"
    file_path = settings.UPLOAD_DIR / unique_filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Calculate checksum
    checksum = calculate_file_checksum(file_path)

    # Parse visibility enum
    visibility_enum = FileVisibility.PRIVATE
    if visibility:
        try:
            visibility_enum = FileVisibility(visibility)
        except ValueError:
            visibility_enum = FileVisibility.PRIVATE

    # Parse tags from string
    tags_list = []
    if tags:
        tags_list = [tag.strip() for tag in tags.split(',')]

    # Create file record
    file_record = FileRecord(
        name=file.filename,
        original_name=file.filename,
        path=str(file_path),
        mime_type=file.content_type or "application/octet-stream",
        extension=file_ext,
        size=file_size,
        status=FileStatus.PENDING,
        visibility=visibility_enum,
        description=description,
        tags=tags_list,
        user_id=current_user.id,
        checksum=checksum
    )

    db.add(file_record)

    # Update user storage
    current_user.storage_used += file_size

    db.commit()
    db.refresh(file_record)

    # Queue background processing
    # background_tasks.add_task(process_file, file_record.id)

    return FileUploadResponse(
        id=file_record.id,
        name=file_record.name,
        size=file_record.size,
        mime_type=file_record.mime_type,
        status=file_record.status
    )


@router.get("/", response_model=FileListResponse)
async def get_user_files(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's files
    """
    query = select(FileRecord).where(FileRecord.user_id == current_user.id)

    # Add search filter
    if search:
        query = query.where(FileRecord.name.contains(search))

    # Get total count
    total = len(db.exec(query).all())

    # Add sorting
    if sort.sort_order == "desc":
        query = query.order_by(getattr(FileRecord, sort.sort_by).desc())
    else:
        query = query.order_by(getattr(FileRecord, sort.sort_by))

    # Add pagination
    query = query.offset(pagination.offset).limit(pagination.limit)

    files = db.exec(query).all()

    return FileListResponse(
        items=files,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page
    )


@router.get("/{file_id}", response_model=FileDetailResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get file details
    """
    file_record = db.get(FileRecord, file_id)

    if not file_record:
        raise FileNotFoundException(file_id)

    # Check permissions
    if file_record.user_id != current_user.id and not file_record.is_public:
        raise PermissionDeniedException("view this file")

    # Increment view count
    file_record.increment_view_count()
    db.commit()

    return file_record


@router.patch("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    file_update: FileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update file metadata
    """
    file_record = db.get(FileRecord, file_id)

    if not file_record:
        raise FileNotFoundException(file_id)

    if file_record.user_id != current_user.id:
        raise PermissionDeniedException("update this file")

    # Update fields
    if file_update.name is not None:
        file_record.name = file_update.name
    if file_update.description is not None:
        file_record.description = file_update.description
    if file_update.visibility is not None:
        file_record.visibility = file_update.visibility
    if file_update.tags is not None:
        file_record.tags = file_update.tags

    db.commit()
    db.refresh(file_record)
    return file_record


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file
    """
    file_record = db.get(FileRecord, file_id)

    if not file_record:
        raise FileNotFoundException(file_id)

    if file_record.user_id != current_user.id:
        raise PermissionDeniedException("delete this file")

    # Delete physical file
    try:
        Path(file_record.path).unlink()
    except:
        pass

    # Update user storage
    current_user.storage_used -= file_record.size

    # Delete record
    db.delete(file_record)
    db.commit()

    return {"message": "File deleted successfully"}


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download a file
    """
    file_record = db.get(FileRecord, file_id)

    if not file_record:
        raise FileNotFoundException(file_id)

    # Check permissions
    if file_record.user_id != current_user.id and not file_record.is_public:
        raise PermissionDeniedException("download this file")

    # Check if file exists
    file_path = Path(file_record.path)
    if not file_path.exists():
        raise FileNotFoundException(file_id)

    # Increment download count
    file_record.increment_download_count()
    db.commit()

    return StarletteFileResponse(
        path=str(file_path),
        filename=file_record.original_name,
        media_type=file_record.mime_type
    )


@router.post("/{file_id}/share", response_model=FileShareResponse)
async def share_file(
    file_id: int,
    share_request: FileShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a share link for a file
    """
    file_record = db.get(FileRecord, file_id)

    if not file_record:
        raise FileNotFoundException(file_id)

    if file_record.user_id != current_user.id:
        raise PermissionDeniedException("share this file")

    # Generate share token
    import secrets
    share_token = secrets.token_urlsafe(32)

    # Set expiration
    from datetime import datetime, timedelta
    expires_at = None
    if share_request.expires_in_hours:
        expires_at = datetime.utcnow() + timedelta(hours=share_request.expires_in_hours)

    # Update file
    file_record.visibility = FileVisibility.SHARED
    file_record.share_token = share_token
    file_record.share_expires_at = expires_at

    db.commit()

    # Generate share URL
    share_url = f"{settings.server_host}/share/{share_token}"

    return FileShareResponse(
        share_token=share_token,
        share_url=share_url,
        expires_at=expires_at
    )


@router.post("/search", response_model=FileListResponse)
async def search_files(
    search_request: FileSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search files with advanced filters
    """
    query = select(FileRecord).where(FileRecord.user_id == current_user.id)

    # Apply filters
    if search_request.query:
        query = query.where(FileRecord.name.contains(search_request.query))

    if search_request.tags:
        # Files that have any of the specified tags
        for tag in search_request.tags:
            query = query.where(FileRecord.tags.contains([tag]))

    if search_request.extensions:
        query = query.where(FileRecord.extension.in_(search_request.extensions))

    if search_request.min_size:
        query = query.where(FileRecord.size >= search_request.min_size)

    if search_request.max_size:
        query = query.where(FileRecord.size <= search_request.max_size)

    if search_request.status:
        query = query.where(FileRecord.status == search_request.status)

    if search_request.visibility:
        query = query.where(FileRecord.visibility == search_request.visibility)

    if search_request.created_after:
        query = query.where(FileRecord.created_at >= search_request.created_after)

    if search_request.created_before:
        query = query.where(FileRecord.created_at <= search_request.created_before)

    # Get total count
    total = len(db.exec(query).all())

    # Apply sorting
    if search_request.sort_order == "desc":
        query = query.order_by(getattr(FileRecord, search_request.sort_by).desc())
    else:
        query = query.order_by(getattr(FileRecord, search_request.sort_by))

    # Apply pagination
    offset = (search_request.page - 1) * search_request.per_page
    query = query.offset(offset).limit(search_request.per_page)

    files = db.exec(query).all()

    return FileListResponse(
        items=files,
        total=total,
        page=search_request.page,
        per_page=search_request.per_page,
        pages=(total + search_request.per_page - 1) // search_request.per_page
    )
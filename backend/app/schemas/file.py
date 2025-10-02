from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.file import FileStatus, FileVisibility


class FileBase(BaseModel):
    """Base file schema"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    visibility: FileVisibility = FileVisibility.PRIVATE
    tags: List[str] = []


class FileCreate(FileBase):
    """Schema for file creation (metadata only, file uploaded separately)"""
    pass


class FileUpdate(BaseModel):
    """Schema for file update"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    visibility: Optional[FileVisibility] = None
    tags: Optional[List[str]] = None


class FileResponse(FileBase):
    """Schema for file response"""
    id: int
    original_name: str
    mime_type: str
    extension: str
    size: int
    size_mb: float
    status: FileStatus
    url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    download_count: int = 0
    view_count: int = 0
    version: int = 1
    checksum: Optional[str] = None

    # 3D model specific
    vertices_count: Optional[int] = None
    faces_count: Optional[int] = None
    materials_count: Optional[int] = None
    textures_count: Optional[int] = None
    animations_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class FileDetailResponse(FileResponse):
    """Detailed file response with additional metadata"""
    file_metadata: Dict[str, Any] = {}
    bounding_box: Optional[Dict[str, List[float]]] = None
    preview_paths: List[str] = []
    share_token: Optional[str] = None
    share_expires_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Response after file upload"""
    id: int
    name: str
    size: int
    mime_type: str
    status: FileStatus
    message: str = "File uploaded successfully"

    model_config = ConfigDict(from_attributes=True)


class FileShareRequest(BaseModel):
    """Request to share a file"""
    expires_in_hours: Optional[int] = Field(None, ge=1, le=720)  # Max 30 days


class FileShareResponse(BaseModel):
    """Response with file sharing information"""
    share_token: str
    share_url: str
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FileConversionRequest(BaseModel):
    """Request to convert file format"""
    target_format: str = Field(..., max_length=20)
    options: Dict[str, Any] = {}

    @field_validator("target_format")
    def validate_format(cls, v):
        allowed_formats = ["gltf", "glb", "obj", "fbx", "stl", "dae", "ply", "usdz"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"Unsupported format. Allowed: {', '.join(allowed_formats)}")
        return v.lower()


class FileConversionResponse(BaseModel):
    """Response for file conversion status"""
    id: int
    source_file_id: int
    target_format: str
    status: FileStatus
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FileBulkOperation(BaseModel):
    """Schema for bulk file operations"""
    file_ids: List[int]
    operation: str  # delete, update_visibility, add_tags, remove_tags

    @field_validator("operation")
    def validate_operation(cls, v):
        allowed_ops = ["delete", "update_visibility", "add_tags", "remove_tags"]
        if v not in allowed_ops:
            raise ValueError(f"Invalid operation. Allowed: {', '.join(allowed_ops)}")
        return v


class FileSearchRequest(BaseModel):
    """Schema for file search"""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    extensions: Optional[List[str]] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    status: Optional[FileStatus] = None
    visibility: Optional[FileVisibility] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

    @field_validator("sort_by")
    def validate_sort_by(cls, v):
        allowed = ["created_at", "updated_at", "name", "size", "download_count", "view_count"]
        if v not in allowed:
            raise ValueError(f"Invalid sort_by. Allowed: {', '.join(allowed)}")
        return v

    @field_validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


class FileListResponse(BaseModel):
    """Response for paginated file list"""
    items: List[FileResponse]
    total: int
    page: int
    per_page: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class FileCommentCreate(BaseModel):
    """Schema for creating a file comment"""
    content: str = Field(..., min_length=1, max_length=1000)


class FileCommentResponse(BaseModel):
    """Schema for file comment response"""
    id: int
    file_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
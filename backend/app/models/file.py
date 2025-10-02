from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, JSON as SQLAlchemyJSON, Text, Index


class FileStatus(str, Enum):
    """File processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class FileVisibility(str, Enum):
    """File visibility settings"""
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"


class FileRecord(SQLModel, table=True):
    """Database model for uploaded files"""
    __tablename__ = "files"
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_status", "status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # File information
    name: str = Field(max_length=255, index=True)
    original_name: str = Field(max_length=255)
    path: str = Field(max_length=500)  # Local storage path
    url: Optional[str] = Field(default=None, max_length=500)  # Public URL if available
    mime_type: str = Field(max_length=100)
    extension: str = Field(max_length=20)
    size: int  # File size in bytes

    # Processing status
    status: FileStatus = Field(default=FileStatus.PENDING)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Visibility and sharing
    visibility: FileVisibility = Field(default=FileVisibility.PRIVATE)
    share_token: Optional[str] = Field(default=None, unique=True, index=True)
    share_expires_at: Optional[datetime] = None

    # File metadata
    file_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(SQLAlchemyJSON)
    )

    # 3D model specific metadata
    vertices_count: Optional[int] = None
    faces_count: Optional[int] = None
    materials_count: Optional[int] = None
    textures_count: Optional[int] = None
    animations_count: Optional[int] = None
    bounding_box: Optional[Dict[str, List[float]]] = Field(
        default=None,
        sa_column=Column(SQLAlchemyJSON)
    )

    # Thumbnails and previews
    thumbnail_path: Optional[str] = Field(default=None, max_length=500)
    preview_paths: List[str] = Field(
        default_factory=list,
        sa_column=Column(SQLAlchemyJSON)
    )

    # Version control
    version: int = Field(default=1)
    parent_file_id: Optional[int] = Field(default=None, foreign_key="files.id")

    # User relationship
    user_id: int = Field(foreign_key="users.id", index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Download/view statistics
    download_count: int = Field(default=0)
    view_count: int = Field(default=0)

    # Tags for categorization
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(SQLAlchemyJSON)
    )

    # Description and notes
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Checksum for integrity
    checksum: Optional[str] = Field(default=None, max_length=64)  # SHA256

    # Relationships
    user: Optional["User"] = Relationship(back_populates="files")
    conversions: List["FileConversion"] = Relationship(back_populates="source_file")
    comments: List["FileComment"] = Relationship(back_populates="file")

    @property
    def is_public(self) -> bool:
        """Check if file is publicly accessible"""
        return self.visibility == FileVisibility.PUBLIC

    @property
    def is_shared(self) -> bool:
        """Check if file has active sharing"""
        if self.visibility != FileVisibility.SHARED:
            return False
        if not self.share_expires_at:
            return True
        return self.share_expires_at > datetime.utcnow()

    @property
    def size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.size / (1024 * 1024)

    def increment_view_count(self):
        """Increment view counter"""
        self.view_count += 1
        self.accessed_at = datetime.utcnow()

    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
        self.accessed_at = datetime.utcnow()


class FileConversion(SQLModel, table=True):
    """Track file format conversions"""
    __tablename__ = "file_conversions"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_file_id: int = Field(foreign_key="files.id")
    target_format: str = Field(max_length=20)
    output_path: str = Field(max_length=500)
    status: FileStatus = Field(default=FileStatus.PENDING)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Relationship
    source_file: Optional[FileRecord] = Relationship(back_populates="conversions")


class FileComment(SQLModel, table=True):
    """Comments on files"""
    __tablename__ = "file_comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="files.id")
    user_id: int = Field(foreign_key="users.id")
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    file: Optional[FileRecord] = Relationship(back_populates="comments")
    user: Optional["User"] = Relationship()
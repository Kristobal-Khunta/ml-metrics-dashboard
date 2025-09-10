from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)
class UploadedFile(SQLModel, table=True):
    """Represents an uploaded data file"""

    __tablename__ = "uploaded_files"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(ge=0)  # Size in bytes
    mime_type: str = Field(max_length=100)
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_processed: bool = Field(default=False)

    # Relationship to datasets contained in this file
    datasets: List["Dataset"] = Relationship(back_populates="uploaded_file")


class Dataset(SQLModel, table=True):
    """Represents a dataset extracted from an uploaded file"""

    __tablename__ = "datasets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(default="", max_length=1000)
    uploaded_file_id: int = Field(foreign_key="uploaded_files.id")

    # Store the actual data points as JSON
    data_points: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Metadata about the dataset structure
    x_column: str = Field(max_length=100)  # Name of X-axis column
    y_column: str = Field(max_length=100)  # Name of Y-axis column
    x_axis_label: str = Field(default="", max_length=100)
    y_axis_label: str = Field(default="", max_length=100)

    # Statistical information
    total_points: int = Field(default=0, ge=0)
    min_x_value: Optional[Decimal] = Field(default=None)
    max_x_value: Optional[Decimal] = Field(default=None)
    min_y_value: Optional[Decimal] = Field(default=None)
    max_y_value: Optional[Decimal] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationship back to uploaded file
    uploaded_file: UploadedFile = Relationship(back_populates="datasets")


class DatasetSelection(SQLModel, table=True):
    """Tracks which dataset is currently selected for display"""

    __tablename__ = "dataset_selections"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="datasets.id")
    selected_at: datetime = Field(default_factory=datetime.utcnow)
    is_current: bool = Field(default=True)

    # Optional session or user identifier for multi-user scenarios
    session_id: Optional[str] = Field(default=None, max_length=100)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UploadedFileCreate(SQLModel, table=False):
    """Schema for creating a new uploaded file record"""

    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(ge=0)
    mime_type: str = Field(max_length=100)


class UploadedFileResponse(SQLModel, table=False):
    """Schema for uploaded file API responses"""

    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_timestamp: str  # ISO format string
    is_processed: bool
    dataset_count: int = Field(default=0)


class DatasetCreate(SQLModel, table=False):
    """Schema for creating a new dataset"""

    name: str = Field(max_length=255)
    description: str = Field(default="", max_length=1000)
    uploaded_file_id: int
    data_points: List[Dict[str, Any]] = Field(default=[])
    x_column: str = Field(max_length=100)
    y_column: str = Field(max_length=100)
    x_axis_label: str = Field(default="", max_length=100)
    y_axis_label: str = Field(default="", max_length=100)


class DatasetUpdate(SQLModel, table=False):
    """Schema for updating dataset properties"""

    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    x_axis_label: Optional[str] = Field(default=None, max_length=100)
    y_axis_label: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class DatasetResponse(SQLModel, table=False):
    """Schema for dataset API responses"""

    id: int
    name: str
    description: str
    uploaded_file_id: int
    x_column: str
    y_column: str
    x_axis_label: str
    y_axis_label: str
    total_points: int
    min_x_value: Optional[Decimal]
    max_x_value: Optional[Decimal]
    min_y_value: Optional[Decimal]
    max_y_value: Optional[Decimal]
    created_at: str  # ISO format string
    is_active: bool
    uploaded_file_name: Optional[str] = None


class DatasetSelectionCreate(SQLModel, table=False):
    """Schema for selecting a dataset for display"""

    dataset_id: int
    session_id: Optional[str] = Field(default=None, max_length=100)


class GraphDataPoint(SQLModel, table=False):
    """Schema for individual data points in graph format"""

    x: Decimal
    y: Decimal
    label: Optional[str] = None


class GraphData(SQLModel, table=False):
    """Schema for complete graph data response"""

    dataset_id: int
    dataset_name: str
    x_axis_label: str
    y_axis_label: str
    data_points: List[GraphDataPoint]
    total_points: int
    min_x: Optional[Decimal]
    max_x: Optional[Decimal]
    min_y: Optional[Decimal]
    max_y: Optional[Decimal]

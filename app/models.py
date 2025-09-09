from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)


class Project(SQLModel, table=True):
    """Represents a machine learning project."""

    __tablename__ = "projects"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    description: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    metrics: List["Metric"] = Relationship(back_populates="project")
    csv_uploads: List["CsvUpload"] = Relationship(back_populates="project")


class Model(SQLModel, table=True):
    """Represents a machine learning model."""

    __tablename__ = "models"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    version: str = Field(default="1.0", max_length=50)
    description: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    metrics: List["Metric"] = Relationship(back_populates="model")


class Dataset(SQLModel, table=True):
    """Represents a dataset used for training/testing."""

    __tablename__ = "datasets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    version: str = Field(default="1.0", max_length=50)
    description: str = Field(default="", max_length=1000)
    dataset_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    metrics: List["Metric"] = Relationship(back_populates="dataset")


class MetricType(SQLModel, table=True):
    """Represents different types of metrics (accuracy, precision, recall, etc.)."""

    __tablename__ = "metric_types"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    description: str = Field(default="", max_length=500)
    unit: str = Field(default="", max_length=50)  # e.g., "percentage", "seconds", "count"
    higher_is_better: bool = Field(default=True)  # For metric optimization direction
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    metrics: List["Metric"] = Relationship(back_populates="metric_type")


class Metric(SQLModel, table=True):
    """Represents individual metric measurements."""

    __tablename__ = "metrics"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    value: Decimal = Field(decimal_places=6, max_digits=20)
    timestamp: datetime = Field(index=True)
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    project_id: int = Field(foreign_key="projects.id", index=True)
    model_id: int = Field(foreign_key="models.id", index=True)
    dataset_id: int = Field(foreign_key="datasets.id", index=True)
    metric_type_id: int = Field(foreign_key="metric_types.id", index=True)
    csv_upload_id: Optional[int] = Field(foreign_key="csv_uploads.id", index=True)

    # Relationships
    project: Project = Relationship(back_populates="metrics")
    model: Model = Relationship(back_populates="metrics")
    dataset: Dataset = Relationship(back_populates="metrics")
    metric_type: MetricType = Relationship(back_populates="metrics")
    csv_upload: Optional["CsvUpload"] = Relationship(back_populates="metrics")


class CsvUpload(SQLModel, table=True):
    """Tracks CSV file uploads and their processing status."""

    __tablename__ = "csv_uploads"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    file_size: int = Field(ge=0)  # File size in bytes
    status: str = Field(default="pending", max_length=50)  # pending, processing, completed, failed
    error_message: str = Field(default="", max_length=2000)
    rows_processed: int = Field(default=0, ge=0)
    rows_failed: int = Field(default=0, ge=0)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    project_id: int = Field(foreign_key="projects.id", index=True)

    # Relationships
    project: Project = Relationship(back_populates="csv_uploads")
    metrics: List[Metric] = Relationship(back_populates="csv_upload")


# Non-persistent schemas (for validation, forms, API requests/responses)


class ProjectCreate(SQLModel, table=False):
    """Schema for creating a new project."""

    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=1000)


class ProjectUpdate(SQLModel, table=False):
    """Schema for updating an existing project."""

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)


class ModelCreate(SQLModel, table=False):
    """Schema for creating a new model."""

    name: str = Field(max_length=100)
    version: str = Field(default="1.0", max_length=50)
    description: str = Field(default="", max_length=1000)


class ModelUpdate(SQLModel, table=False):
    """Schema for updating an existing model."""

    name: Optional[str] = Field(default=None, max_length=100)
    version: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=1000)


class DatasetCreate(SQLModel, table=False):
    """Schema for creating a new dataset."""

    name: str = Field(max_length=100)
    version: str = Field(default="1.0", max_length=50)
    description: str = Field(default="", max_length=1000)
    dataset_metadata: Dict[str, Any] = Field(default={})


class DatasetUpdate(SQLModel, table=False):
    """Schema for updating an existing dataset."""

    name: Optional[str] = Field(default=None, max_length=100)
    version: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=1000)
    dataset_metadata: Optional[Dict[str, Any]] = Field(default=None)


class MetricTypeCreate(SQLModel, table=False):
    """Schema for creating a new metric type."""

    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    unit: str = Field(default="", max_length=50)
    higher_is_better: bool = Field(default=True)


class MetricTypeUpdate(SQLModel, table=False):
    """Schema for updating an existing metric type."""

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    unit: Optional[str] = Field(default=None, max_length=50)
    higher_is_better: Optional[bool] = Field(default=None)


class MetricCreate(SQLModel, table=False):
    """Schema for creating a new metric."""

    value: Decimal = Field(decimal_places=6, max_digits=20)
    timestamp: datetime
    notes: str = Field(default="", max_length=1000)
    project_id: int
    model_id: int
    dataset_id: int
    metric_type_id: int
    csv_upload_id: Optional[int] = None


class MetricUpdate(SQLModel, table=False):
    """Schema for updating an existing metric."""

    value: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=20)
    timestamp: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=1000)


class CsvUploadCreate(SQLModel, table=False):
    """Schema for creating a new CSV upload record."""

    filename: str = Field(max_length=255)
    file_size: int = Field(ge=0)
    project_id: int


class CsvUploadUpdate(SQLModel, table=False):
    """Schema for updating CSV upload status."""

    status: Optional[str] = Field(default=None, max_length=50)
    error_message: Optional[str] = Field(default=None, max_length=2000)
    rows_processed: Optional[int] = Field(default=None, ge=0)
    rows_failed: Optional[int] = Field(default=None, ge=0)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None


# CSV Row Schema for validation
class CsvRowData(SQLModel, table=False):
    """Schema for validating CSV row data."""

    project: str = Field(max_length=100)
    model: str = Field(max_length=100)
    dataset: str = Field(max_length=100)
    metric_name: str = Field(max_length=100)
    metric_value: Decimal = Field(decimal_places=6, max_digits=20)
    timestamp: datetime


# Response schemas for API/UI
class MetricResponse(SQLModel, table=False):
    """Response schema for metric data with related information."""

    id: int
    value: Decimal
    timestamp: datetime
    notes: str
    created_at: datetime
    project_name: str
    model_name: str
    model_version: str
    dataset_name: str
    dataset_version: str
    metric_type_name: str
    metric_type_unit: str
    metric_type_higher_is_better: bool


class ProjectSummary(SQLModel, table=False):
    """Summary information for a project."""

    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    total_metrics: int
    total_models: int
    total_datasets: int
    latest_metric_timestamp: Optional[datetime] = None


class MetricSummary(SQLModel, table=False):
    """Summary for a specific metric type within a project."""

    metric_type_name: str
    metric_type_unit: str
    latest_value: Decimal
    latest_timestamp: datetime
    model_name: str
    dataset_name: str
    trend_direction: str  # "up", "down", "stable"
    change_percentage: Optional[Decimal] = None


# Filter schemas for dashboard queries
class MetricFilter(SQLModel, table=False):
    """Filter criteria for metric queries."""

    project_ids: Optional[List[int]] = None
    model_ids: Optional[List[int]] = None
    dataset_ids: Optional[List[int]] = None
    metric_type_ids: Optional[List[int]] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    limit: Optional[int] = Field(default=1000, le=10000)

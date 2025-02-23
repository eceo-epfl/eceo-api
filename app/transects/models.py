from sqlmodel import (
    SQLModel,
    Field,
    UniqueConstraint,
    Relationship,
    Column,
)
from pydantic import model_validator
from typing import Any, TYPE_CHECKING
from uuid import uuid4, UUID
import datetime
from sqlalchemy.sql import func
from geoalchemy2 import Geometry, WKBElement
import shapely

if TYPE_CHECKING:
    from app.objects.models.inputs import InputObject
    from app.submissions.models import Submission


class TransectBase(SQLModel):
    name: str
    description: str | None = None
    length: float | None = Field(None, ge=0)
    depth: float | None = Field(None, ge=0)
    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        title="Created On",
        description="Date and time when the record was created",
        sa_column_kwargs={"default": func.now()},
    )

    last_updated: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        title="Last Updated",
        description="Date and time when the record was last updated",
        sa_column_kwargs={
            "onupdate": func.now(),
            "server_default": func.now(),
        },
    )


class Transect(TransectBase, table=True):
    __table_args__ = (
        UniqueConstraint("id"),
        UniqueConstraint("name"),
    )
    iterator: int = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )

    id: UUID = Field(
        default_factory=uuid4,
        index=True,
        nullable=False,
    )
    geom: Any = Field(
        default=None,
        sa_column=Column(
            Geometry("LINESTRING", srid=4326),
        ),
    )
    owner: UUID = Field(
        nullable=False,
        index=True,
    )

    inputs: list["InputObject"] = Relationship(
        back_populates="transect",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    submissions: list["Submission"] = Relationship(
        back_populates="transect",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TransectCreate(TransectBase):
    latitude_start: float = Field(ge=-90, le=90)
    longitude_start: float = Field(ge=-180, le=180)
    latitude_end: float = Field(ge=-90, le=90)
    longitude_end: float = Field(ge=-180, le=180)

    geom: Any | None = None

    @model_validator(mode="after")
    def convert_lat_lon_to_wkt(cls, values: Any) -> Any:
        """Convert the lat/lon coordinates to a WKT geometry"""

        # Encode the SRID into the WKT
        values.geom = shapely.wkt.dumps(
            shapely.geometry.LineString(
                [
                    (values.longitude_start, values.latitude_start),
                    (values.longitude_end, values.latitude_end),
                ]
            )
        )

        return values


class SubmissionReadSimple(SQLModel):
    id: UUID
    name: str | None = None
    time_added_utc: datetime.datetime
    run_status: list[Any] = []


class TransectRead(TransectBase):
    id: UUID
    geom: Any | None = None
    owner: UUID
    latitude_start: float | None = Field(None, ge=-90, le=90)
    longitude_start: float | None = Field(None, ge=-180, le=180)

    latitude_end: float | None = Field(None, ge=-90, le=90)
    longitude_end: float | None = Field(None, ge=-180, le=180)

    inputs: list[Any] = []
    submissions: list[SubmissionReadSimple] = []

    @model_validator(mode="after")
    def convert_wkb_to_lat_long(
        cls,
        values: "TransectRead",
    ) -> dict:
        """Form the lat/lon geom from the start and end of the line string"""

        if isinstance(values.geom, WKBElement):
            if values.geom is not None:
                shapely_obj = shapely.wkb.loads(str(values.geom))
                if shapely_obj is not None:
                    mapping = shapely.geometry.mapping(shapely_obj)
                    values.latitude_start = mapping["coordinates"][0][1]
                    values.longitude_start = mapping["coordinates"][0][0]
                    values.latitude_end = mapping["coordinates"][-1][1]
                    values.longitude_end = mapping["coordinates"][-1][0]
                    values.geom = mapping

        elif isinstance(values.geom, dict):
            if values.geom is not None:
                values.latitude_start = values.geom["coordinates"][0][1]
                values.longitude_start = values.geom["coordinates"][0][0]
                values.latitude_end = values.geom["coordinates"][-1][1]
                values.longitude_end = values.geom["coordinates"][-1][0]

                values.geom = values.geom

        else:
            values.latitude_start = None
            values.longitude_start = None
            values.latitude_end = None
            values.longitude_end = None

        return values


class TransectUpdate(TransectCreate):
    pass

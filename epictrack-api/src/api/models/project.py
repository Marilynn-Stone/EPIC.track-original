# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Model to manage Project."""
import enum

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from .base_model import BaseModelVersioned


class ProjectStateEnum(enum.Enum):
    """Enum for project state"""

    POTENTIAL_WORK = 1
    PRE_WORK = 2
    UNDER_WORK = 3
    WORK_PENDING = 4
    UNDER_DISPUTE_RESOLUTION = 5
    OTHER_WORK = 6
    PROJECT_WITHDRAWN = 7
    PROJECT_TERMINATED = 8
    EAC_EXPIRED = 9
    EAC_OR_ORDER_CANCELLED = 10
    EAC_OR_ORDER_SUSPENDED = 11
    INDETERMINATE = 12
    PRECONSTRUCTION = 13
    CONSTRUCTION = 14
    OPERATION = 15
    CARE_AND_MAINTENANCE = 16
    DECOMMISSIONING = 17
    CLOSED = 18


class Project(BaseModelVersioned):
    """Model class for Project."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String())
    project_tracking_number = Column(String(), nullable=True, default=None)
    description = Column(String())
    latitude = Column(String(), nullable=False)
    longitude = Column(String(), nullable=False)
    capital_investment = Column(Float())
    epic_guid = Column(String(), nullable=True, default=None)
    is_project_closed = Column(Boolean(), default=False, nullable=False)
    address = Column(Text, nullable=True, default=None)
    fte_positions_construction = Column(Integer(), nullable=True)
    fte_positions_operation = Column(Integer(), nullable=True)

    ea_certificate = Column(String(255), nullable=True, default=None)
    sub_type_id = Column(ForeignKey("sub_types.id"), nullable=False)
    type_id = Column(ForeignKey("types.id"), nullable=False)
    proponent_id = Column(ForeignKey("proponents.id"), nullable=False)
    region_id_env = Column(ForeignKey("regions.id"), nullable=True)
    region_id_flnro = Column(ForeignKey("regions.id"), nullable=True)
    abbreviation = Column(String(10), nullable=True, unique=True)
    eac_signed = Column(Date(), nullable=True)
    eac_expires = Column(Date(), nullable=True)
    project_state_id = Column(ForeignKey("project_states.id", name="projects_project_state_id_project_state_fk"))
    sub_type = relationship("SubType", foreign_keys=[sub_type_id], lazy="select")
    type = relationship("Type", foreign_keys=[type_id], lazy="select")
    proponent = relationship("Proponent", foreign_keys=[proponent_id], lazy="select")
    region_env = relationship("Region", foreign_keys=[region_id_env], lazy="select")
    region_flnro = relationship("Region", foreign_keys=[region_id_flnro], lazy="select")
    works = relationship('Work', lazy='dynamic')

    @classmethod
    def find_all_projects(cls, with_works=False, is_active=None):
        """Return all projects with works."""
        query = cls.query
        if with_works:
            query = query.filter(cls.works.any())
        if is_active is not None:
            query = query.filter(cls.is_active.is_(is_active))
        return query.filter(cls.is_deleted.is_(False)).all()

    @classmethod
    def check_existence(cls, name, project_id=None):
        """Checks if a project exists with given name"""
        query = Project.query.filter(
            func.lower(Project.name) == func.lower(name), Project.is_deleted.is_(False)
        )
        if project_id:
            query = query.filter(Project.id != project_id)
        if query.count() > 0:
            return True
        return False

    @classmethod
    def get_by_abbreviation(cls, abbreviation: str):
        """Get project by abbreviation."""
        return Project.query.filter_by(abbreviation=abbreviation).first()

    def as_dict(self, recursive=True):
        """Return JSON Representation."""
        data = super().as_dict(recursive)
        return data

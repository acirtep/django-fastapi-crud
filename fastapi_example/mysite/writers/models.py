from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from mysite.models import Base


class Writer(Base):
    __tablename__ = "fastapi_writer"
    __table_args__ = {"comment": "general information about writers"}

    writer_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text(
            "gen_random_uuid()",
        ),
        comment="unique identifier of the writer",
    )
    first_name = Column(String, comment="the first name of the writer")
    last_name = Column(String, comment="the last name of the writer")
    email = Column(String, nullable=False, unique=True, comment="the email of the writer")
    about = Column(String, comment="a short intro of the writer")
    joined_timestamp = Column(
        DateTime(timezone=True),
        server_default=text("statement_timestamp()"),
        nullable=False,
        comment="the date time in UTC, when the writer joined",
    )

    partner_program = relationship(
        "WriterPartnerProgram", back_populates="writer", viewonly=True, uselist=False, lazy="joined"
    )
    partner_program_status = association_proxy(target_collection="partner_program", attr="active")


class WriterPartnerProgram(Base):
    __tablename__ = "fastapi_partner_program"
    __table_args__ = {"comment": "information about partner program at writer level"}

    writer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fastapi_writer.writer_id", ondelete="CASCADE"),
        primary_key=True,
        comment="unique identifier of the writer",
    )
    writer = relationship(Writer, passive_deletes=True, back_populates="partner_program", single_parent=True)

    joined_timestamp = Column(
        DateTime(timezone=True),
        server_default=text("statement_timestamp()"),
        nullable=False,
        comment="the date time in UTC, when the writer joined the partner program",
    )
    payment_method = Column(
        String,
        nullable=False,
        comment="the payment method of the partner program, eg: stripe",
    )
    country_code = Column(String, nullable=False, comment="the country iso code of the writer")
    active = Column(
        Boolean, nullable=False, server_default=expression.true(), comment="true if the partner program is active"
    )

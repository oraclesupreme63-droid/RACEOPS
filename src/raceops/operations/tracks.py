"""Application services for team-scoped Track management."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from raceops.iam.errors import ResourceNotFoundError
from raceops.iam.identity import CurrentIdentity
from raceops.operations.models import Track


def create_track(
    session: Session,
    actor: CurrentIdentity,
    *,
    name: str,
    location: str | None,
) -> Track:
    """Create one minimal Track inside the actor's selected Team."""
    track = Track(team_id=actor.team_id, name=name, location=location)
    session.add(track)
    session.commit()
    session.refresh(track)
    return track


def list_tracks(
    session: Session,
    actor: CurrentIdentity,
    *,
    limit: int,
    offset: int,
) -> tuple[list[Track], int]:
    """List Tracks only inside the actor's selected Team."""
    filters = [Track.team_id == actor.team_id]
    total = session.scalar(select(func.count()).select_from(Track).where(*filters))
    statement = (
        select(Track)
        .where(*filters)
        .order_by(Track.created_at, Track.track_id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def get_track(
    session: Session,
    actor: CurrentIdentity,
    track_id: UUID,
) -> Track:
    """Read one same-Team Track without revealing foreign resources."""
    track = session.scalar(
        select(Track).where(
            Track.track_id == track_id,
            Track.team_id == actor.team_id,
        )
    )
    if track is None:
        raise ResourceNotFoundError
    return track


def update_track(
    session: Session,
    actor: CurrentIdentity,
    track_id: UUID,
    *,
    change_name: bool,
    name: str | None,
    change_location: bool,
    location: str | None,
) -> Track:
    """Update permitted Track metadata while preserving Team ownership."""
    track = _get_track_for_update(session, actor.team_id, track_id)
    if change_name:
        if name is None:
            raise ValueError("name is required when changed")
        track.name = name
    if change_location:
        track.location = location
    session.commit()
    session.refresh(track)
    return track


def _get_track_for_update(
    session: Session,
    team_id: UUID,
    track_id: UUID,
) -> Track:
    track = session.scalar(
        select(Track)
        .where(
            Track.track_id == track_id,
            Track.team_id == team_id,
        )
        .with_for_update()
    )
    if track is None:
        raise ResourceNotFoundError
    return track

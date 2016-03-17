# Copyright 2016 PLUMgrid Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Implementation of SQLAlchemy backend.'''
import sys

from networking_plumgrid._i18n import _LW
from networking_plumgrid.neutron.plugins.common import exceptions as exception
from networking_plumgrid.neutron.plugins.db.sqlal import models
from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
import sqlalchemy

from oslo_log import log as logging
LOG = logging.getLogger(__name__)

CONF = cfg.CONF

_facade = None


def get_facade():
    global _facade

    if not _facade:
        _facade = db_session.EngineFacade.from_config(CONF)
    return _facade

get_engine = lambda: get_facade().get_engine()
get_session = lambda: get_facade().get_session()


def create_table_pg_lock():
    try:
        meta = sqlalchemy.MetaData()
        meta.bind = get_engine()

        pg_lock = sqlalchemy.Table(
            'pg_lock', meta,
            sqlalchemy.Column('uuid', sqlalchemy.String(length=36),
                              primary_key=True,
                              nullable=False),
            sqlalchemy.Column('created_at', sqlalchemy.DateTime),
            sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
            mysql_engine='InnoDB',
            mysql_charset='utf8'
        )
        pg_lock.create()
    except Exception:
        pass


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def model_query(context, *args):
    session = _session(context)
    query = session.query(*args)
    return query


def soft_delete_aware_query(context, *args, **kwargs):
    """Stack query helper that accounts for context's `show_deleted` field.

    :param show_deleted: if True, overrides context's show_deleted field.
    """

    query = model_query(context, *args)
    show_deleted = kwargs.get('show_deleted') or context.show_deleted

    if not show_deleted:
        query = query.filter_by(deleted_at=None)
    return query


def _session(context):
    return (context and context.session) or get_session()


def pg_lock_create(uuid):
    try:
        session = get_session()
        with session.begin():
            lock = session.query(models.PGLock).get(uuid)
            if lock is not None:
                return lock.uuid
            session.add(models.PGLock(uuid=uuid))
            LOG.debug("Lock acquired for resource: " + uuid)
    except:  # noqa
        LOG.warning(_LW("Lock contest, sending back to re-try: %s"), uuid)
        raise exception.TenantResourcesInUse


def pg_lock_get(uuid):
    try:
        import datetime
        current_time = datetime.datetime.utcnow()
        two_min_ago = current_time - datetime.timedelta(minutes=2)
        session = get_session()
        with session.begin():
            res = session.query(models.PGLock).filter(
                  models.PGLock.created_at < two_min_ago).all()
            return res
    except:  # noqa
        return None


def pg_lock_get_id(uuid):
    session = get_session()
    with session.begin():
        lock = session.query(models.PGLock).get(uuid)
        if lock is not None:
            return lock.uuid


def pg_lock_steal(uuid):
    session = get_session()
    with session.begin():
        rows_affected = session.query(
            models.PGLock
        ).filter_by(uuid=uuid).delete()
    if not rows_affected:
        return True


def pg_lock_release(uuid):
    session = get_session()
    with session.begin():
        rows_affected = session.query(
            models.PGLock
        ).filter_by(uuid=uuid).delete()
    if not rows_affected:
        return True

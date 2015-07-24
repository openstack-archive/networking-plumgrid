#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib

from oslo_log import log as logging
from oslo_utils import excutils

from networking_plumgrid.neutron.plugins.common import exceptions as exception
from neutron.i18n import _LI, _LW
from networking_plumgrid.neutron.plugins.common.locking import lock_object

LOG = logging.getLogger(__name__)


class PGLock(object):
    def __init__(self, context, uuid):
        self.context = context
        self.uuid = uuid
        self.listener = None

    @staticmethod
    def get_lock_id(self):
        return lock_object.PGLock.get_lock_id(self.uuid)

    def try_acquire(self):
        """
        Try to acquire a stack lock, but don't raise an ActionInProgress
        exception or try to steal lock.
        """
        return lock_object.PGLock.create(self.uuid)

    def acquire(self, retry=True):
        """
        Acquire a lock on the stack.

        :param retry: When True, retry if lock was released while stealing.
        :type retry: boolean
        """
        lock_id = lock_object.PGLock.create(self.uuid)
        if lock_id is None:
            LOG.debug("Engine %(engine)s acquired lock on stack "
                      "%(stack)s" % {'engine': self.uuid,
                                     'stack': self.uuid})
            return

        if (lock_id == self.uuid):
            LOG.debug("Lock on stack %(stack)s is owned by engine "
                      "%(engine)s" % {'stack': self.uuid,
                                      'engine': lock_id})
            err_msg = ("Tenant (" + self.uuid + ") resources are currently in "
                       " use by another session. Please re-try")
            raise exception.TenantResourcesInUse(err_msg=err_msg)
        else:
            LOG.info(_LI("Stale lock detected on stack %(stack)s.  Engine "
                         "%(engine)s will attempt to steal the lock"),
                     {'stack': self.uuid, 'engine': self.uuid})

            result = lock_object.PGLock.steal(self.uuid)

            if result is None:
                LOG.info(_LI("Engine %(engine)s successfully stole the lock "
                             "on stack %(stack)s"),
                         {'engine': self.uuid,
                          'stack': self.uuid})
                return
            elif result is True:
                if retry:
                    LOG.info(_LI("The lock on stack %(stack)s was released "
                                 "while engine %(engine)s was stealing it. "
                                 "Trying again"), {'stack': self.uuid,
                                                   'engine': self.uuid})
                    return self.acquire(retry=False)
            else:
                new_lock_id = result
                LOG.info(_LI("Failed to steal lock on stack %(stack)s. "
                             "Engine %(engine)s stole the lock first"),
                         {'stack': self.uuid,
                          'engine': new_lock_id})

            err_msg = ("Tenant (" + self.uuid + ") resources are currently in "
                       " use by another session. Please re-try")
            raise exception.TenantResourcesInUse(err_msg=err_msg)

    def release(self, uuid):
        """Release a stack lock."""
        # Only the engine that owns the lock will be releasing it.
        result = lock_object.PGLock.release(uuid)
        if result is True:
            LOG.warn(_LW("Lock was already released on stack %s!"), uuid)
        else:
            LOG.debug("Engine %(engine)s released lock on stack "
                      "%(stack)s" % {'engine': self.uuid,
                                     'stack': uuid})

    @contextlib.contextmanager
    def thread_lock(self, uuid):
        """
        Acquire a lock and release it only if there is an exception.  The
        release method still needs to be scheduled to be run at the
        end of the thread using the Thread.link method.
        """
        try:
            self.acquire()
            yield
        except exception.TenantResourcesInUse:
            raise
        except:  # noqa
            with excutils.save_and_reraise_exception():
                self.release(uuid)

    @contextlib.contextmanager
    def try_thread_lock(self, uuid):
        """
        Similar to thread_lock, but acquire the lock using try_acquire
        and only release it upon any exception after a successful
        acquisition.
        """
        result = None
        try:
            result = self.try_acquire()
            yield result
        except:  # noqa
            if result is None:  # Lock was successfully acquired
                with excutils.save_and_reraise_exception():
                    self.release(uuid)
            raise

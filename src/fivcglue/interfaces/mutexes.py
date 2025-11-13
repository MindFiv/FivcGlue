"""Mutex interfaces for distributed locking and synchronization.

This module defines interfaces for mutex (mutual exclusion) locks:
- IMutex: Interface for acquiring and releasing locks
- IMutexSite: Factory interface for creating named mutexes

Mutexes are useful for coordinating access to shared resources across
multiple processes or distributed systems. All mutexes have an expiration
time to prevent deadlocks from crashed processes.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from fivcglue import IComponent

if TYPE_CHECKING:
    from datetime import timedelta


class IMutex(IComponent):
    """Interface for a mutex lock with automatic expiration.

    IMutex provides distributed locking capabilities with automatic expiration
    to prevent deadlocks. Locks can be acquired in blocking or non-blocking mode.

    All locks must have an expiration time. If a process crashes while holding
    a lock, the lock will automatically be released after the expiration time.

    Example:
        >>> from datetime import timedelta
        >>> mutex_site = RedisMutexSiteImpl(_component_site=None)
        >>> mutex = mutex_site.get_mutex("resource:123")
        >>> if mutex.acquire(expire=timedelta(seconds=30), method="blocking"):
        ...     try:
        ...         # Critical section - exclusive access to resource
        ...         process_resource()
        ...     finally:
        ...         mutex.release()
    """

    @abstractmethod
    def acquire(
        self,
        expire: timedelta,
        method: str = "blocking",
    ) -> bool:
        """Attempt to acquire the mutex lock.

        Args:
            expire: Time duration until the lock automatically expires.
                This prevents deadlocks if the process crashes while
                holding the lock. Must be a positive timedelta.
            method: Acquisition method. Options:
                - "blocking": Wait until the lock is acquired
                - "non-blocking": Return immediately if lock cannot be acquired
                Defaults to "blocking".

        Returns:
            True if the lock was successfully acquired, False otherwise.
            For blocking mode, this typically always returns True.
            For non-blocking mode, returns False if the lock is held by another process.
        """

    @abstractmethod
    def release(self) -> bool:
        """Release the mutex lock.

        Should only be called by the process that currently holds the lock.
        Releasing a lock that is not held by the current process may have
        undefined behavior depending on the implementation.

        Returns:
            True if the lock was successfully released, False otherwise.
        """


class IMutexSite(IComponent):
    """Factory interface for creating and managing named mutexes.

    IMutexSite provides a centralized way to create and retrieve mutex instances
    by name. This allows different parts of an application (or different processes)
    to coordinate access to shared resources using the same mutex name.

    Example:
        >>> mutex_site = RedisMutexSiteImpl(_component_site=None, host="localhost")
        >>> user_mutex = mutex_site.get_mutex("user:123:update")
        >>> order_mutex = mutex_site.get_mutex("order:456:process")
    """

    @abstractmethod
    def get_mutex(self, mtx_name: str) -> IMutex | None:
        """Create or retrieve a mutex by name.

        Args:
            mtx_name: Unique name for the mutex. Multiple calls with the same
                name should coordinate on the same underlying lock.

        Returns:
            A mutex instance for the specified name, or None if the mutex
            could not be created.
        """

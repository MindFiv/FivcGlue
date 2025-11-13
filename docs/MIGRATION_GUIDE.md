# Migration Guide: From @implements Decorator to Direct Inheritance

## Overview

FivcGlue has migrated from using the `@implements` decorator pattern to standard Python direct inheritance. This change improves code readability, IDE support, type checking, and follows Python best practices.

## What Changed

### Before (Deprecated)

```python
from fivcglue import utils
from fivcglue.interfaces import caches

@utils.implements(caches.ICache)
class CacheImpl:
    def get_value(self, key_name: str) -> bytes | None:
        ...
    
    def set_value(self, key_name: str, value: bytes | None, expire: timedelta) -> bool:
        ...
```

### After (Recommended)

```python
from fivcglue.interfaces import caches

class CacheImpl(caches.ICache):
    def get_value(self, key_name: str) -> bytes | None:
        ...
    
    def set_value(self, key_name: str, value: bytes | None, expire: timedelta) -> bool:
        ...
```

## Why This Change?

### Benefits of Direct Inheritance

1. **Standard Python Pattern**: Direct inheritance is the conventional way to implement interfaces in Python
2. **Better IDE Support**: IDEs can properly recognize methods, provide autocomplete, and navigate to interface definitions
3. **Improved Type Checking**: Static type checkers (mypy, pyright) understand inheritance natively
4. **Clearer Code**: The inheritance relationship is explicit in the class definition
5. **Better Debugging**: Class names remain as defined (no wrapper classes)
6. **Easier to Learn**: New developers don't need to understand a custom decorator

### What Was Lost?

Nothing! The `@implements` decorator was simply creating inheritance at runtime. Direct inheritance provides the exact same functionality with better tooling support.

## Migration Steps

### For Internal FivcGlue Code

All internal implementations have been migrated. No action needed.

### For External Code Using FivcGlue

If you have custom component implementations using `@utils.implements`, follow these steps:

#### Step 1: Update Class Definition

**Before:**
```python
from fivcglue import utils
from fivcglue.interfaces.caches import ICache

@utils.implements(ICache)
class MyCustomCache:
    pass
```

**After:**
```python
from fivcglue.interfaces.caches import ICache

class MyCustomCache(ICache):
    pass
```

#### Step 2: Remove Unused Import

If you only imported `utils` for the decorator, you can remove that import:

**Before:**
```python
from fivcglue import IComponentSite, utils
from fivcglue.interfaces import caches

@utils.implements(caches.ICache)
class CacheImpl:
    pass
```

**After:**
```python
from fivcglue import IComponentSite
from fivcglue.interfaces import caches

class CacheImpl(caches.ICache):
    pass
```

#### Step 3: Test Your Code

Run your tests to ensure everything still works. The behavior is identical, so all tests should pass without modification.

## Examples

### Cache Implementation

**Before:**
```python
from fivcglue import IComponentSite, utils
from fivcglue.interfaces import caches

@utils.implements(caches.ICache)
class RedisCacheImpl:
    def __init__(self, _component_site: IComponentSite, host: str = "localhost"):
        self.host = host
    
    def get_value(self, key_name: str) -> bytes | None:
        # Implementation
        pass
    
    def set_value(self, key_name: str, value: bytes | None, expire: timedelta) -> bool:
        # Implementation
        pass
```

**After:**
```python
from fivcglue import IComponentSite
from fivcglue.interfaces import caches

class RedisCacheImpl(caches.ICache):
    def __init__(self, _component_site: IComponentSite, host: str = "localhost"):
        self.host = host
    
    def get_value(self, key_name: str) -> bytes | None:
        # Implementation
        pass
    
    def set_value(self, key_name: str, value: bytes | None, expire: timedelta) -> bool:
        # Implementation
        pass
```

### Config Implementation

**Before:**
```python
from fivcglue import IComponentSite, utils
from fivcglue.interfaces import configs

@utils.implements(configs.IConfig)
class CustomConfigImpl:
    def __init__(self, _component_site: IComponentSite):
        pass
    
    def get_session(self, session_name: str) -> configs.IConfigSession | None:
        # Implementation
        pass
```

**After:**
```python
from fivcglue import IComponentSite
from fivcglue.interfaces import configs

class CustomConfigImpl(configs.IConfig):
    def __init__(self, _component_site: IComponentSite):
        pass
    
    def get_session(self, session_name: str) -> configs.IConfigSession | None:
        # Implementation
        pass
```

### Logger Implementation

**Before:**
```python
from fivcglue import IComponentSite, utils
from fivcglue.interfaces import loggers

@utils.implements(loggers.ILogger)
class CustomLoggerImpl:
    def info(self, msg: str = "", attrs: dict | None = None, error: Exception | None = None):
        # Implementation
        pass
    
    def warning(self, msg: str = "", attrs: dict | None = None, error: Exception | None = None):
        # Implementation
        pass
    
    def error(self, msg: str = "", attrs: dict | None = None, error: Exception | None = None):
        # Implementation
        pass
```

**After:**
```python
from fivcglue import IComponentSite
from fivcglue.interfaces import loggers

class CustomLoggerImpl(loggers.ILogger):
    def info(self, msg: str = "", attrs: dict | None = None, error: Exception | None = None):
        # Implementation
        pass
    
    def warning(self, msg: str = "", attrs: dict | None = None, error: Exception | None = None):
        # Implementation
        pass
    
    def error(self, msg: str = "", attrs: dict | None = None, error: Exception | None = None):
        # Implementation
        pass
```

## Deprecation Timeline

- **Current Version**: `@implements` decorator is deprecated but still functional
  - A `DeprecationWarning` is issued when the decorator is used
  - All internal code has been migrated to direct inheritance
  
- **Future Version**: The decorator may be removed in a future major version
  - External code should migrate to direct inheritance before then

## Backward Compatibility

The `@implements` decorator still works and will continue to work for the foreseeable future. However:

1. It now emits a `DeprecationWarning` when used
2. It is no longer used in any internal FivcGlue code
3. New code should use direct inheritance

## FAQ

### Q: Will my existing code break?

**A:** No. The `@implements` decorator still works exactly as before. You'll just see deprecation warnings.

### Q: Do I need to update my code immediately?

**A:** No, but it's recommended. The decorator will continue to work, but direct inheritance provides better tooling support.

### Q: What if I suppress the deprecation warning?

**A:** You can suppress it, but we recommend migrating to direct inheritance instead:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fivcglue.interfaces.utils")
```

### Q: Can I use both patterns in the same codebase?

**A:** Yes, but it's not recommended. For consistency, migrate all implementations to direct inheritance.

### Q: Does this affect component registration?

**A:** No. The component registration system (`ComponentSite.register_component()`) works identically with both patterns.

### Q: Will type checkers work better now?

**A:** Yes! Static type checkers like mypy and pyright understand direct inheritance natively, providing better type checking and error detection.

### Q: What about IDE autocomplete?

**A:** Yes! IDEs can now properly recognize interface methods and provide better autocomplete suggestions.

## Need Help?

If you encounter any issues during migration, please:

1. Check that your class properly inherits from the interface
2. Ensure all abstract methods are implemented
3. Run your tests to verify functionality
4. Check the examples in this guide

For additional support, please open an issue on the FivcGlue repository.

## Summary

The migration from `@implements` decorator to direct inheritance is straightforward:

1. Replace `@utils.implements(IInterface)` with `class MyImpl(IInterface):`
2. Remove unused `utils` import if applicable
3. Test your code (behavior is identical)
4. Enjoy better IDE support and type checking!

This change makes FivcGlue more Pythonic and easier to work with while maintaining full backward compatibility.


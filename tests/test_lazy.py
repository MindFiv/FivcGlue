import unittest

from fivcglue.lazy import LazyValue


class TestLazyValueBasics(unittest.TestCase):
    """Test basic LazyValue functionality"""

    def test_lazy_evaluation(self):
        """Test that value is only computed on first access"""
        call_count = 0

        def getter():
            nonlocal call_count
            call_count += 1
            return 42

        lazy: LazyValue[int] = LazyValue(getter)
        self.assertEqual(call_count, 0, "Getter should not be called on initialization")

        # First access
        value = lazy()
        self.assertEqual(value, 42)
        self.assertEqual(call_count, 1, "Getter should be called once")

        # Second access
        value = lazy()
        self.assertEqual(value, 42)
        self.assertEqual(call_count, 1, "Getter should not be called again (cached)")

    def test_generic_type_int(self):
        """Test LazyValue with int type"""
        lazy: LazyValue[int] = LazyValue(lambda: 100)
        result: int = lazy()
        self.assertEqual(result, 100)
        self.assertIsInstance(result, int)

    def test_generic_type_str(self):
        """Test LazyValue with str type"""
        lazy: LazyValue[str] = LazyValue(lambda: "hello")
        result: str = lazy()
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, str)

    def test_generic_type_list(self):
        """Test LazyValue with list type"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3])
        result: list[int] = lazy()
        self.assertEqual(result, [1, 2, 3])
        self.assertIsInstance(result, list)

    def test_generic_type_dict(self):
        """Test LazyValue with dict type"""
        lazy: LazyValue[dict[str, int]] = LazyValue(lambda: {"a": 1, "b": 2})
        result: dict[str, int] = lazy()
        self.assertEqual(result, {"a": 1, "b": 2})
        self.assertIsInstance(result, dict)

    def test_repr_uninitialized(self):
        """Test repr of uninitialized LazyValue"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        self.assertEqual(repr(lazy), "LazyValue(<uninitialized>)")

    def test_repr_initialized(self):
        """Test repr of initialized LazyValue"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        lazy()  # Initialize
        self.assertEqual(repr(lazy), "LazyValue(42)")

    def test_str(self):
        """Test str conversion"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        self.assertEqual(str(lazy), "42")

    def test_bool_true(self):
        """Test bool conversion for truthy value"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        self.assertTrue(bool(lazy))

    def test_bool_false(self):
        """Test bool conversion for falsy value"""
        lazy: LazyValue[int] = LazyValue(lambda: 0)
        self.assertFalse(bool(lazy))


class TestLazyValueAttributes(unittest.TestCase):
    """Test attribute access delegation"""

    def test_getattr(self):
        """Test getting attributes from underlying value"""
        lazy: LazyValue[str] = LazyValue(lambda: "hello")
        self.assertEqual(lazy.upper(), "HELLO")
        self.assertEqual(lazy.lower(), "hello")

    def test_setattr(self):
        """Test setting attributes on underlying value"""

        class MyClass:
            def __init__(self):
                self.value = 10

        lazy: LazyValue[MyClass] = LazyValue(MyClass)
        lazy.value = 20
        self.assertEqual(lazy.value, 20)

    def test_delattr(self):
        """Test deleting attributes from underlying value"""

        class MyClass:
            def __init__(self):
                self.value = 10

        lazy: LazyValue[MyClass] = LazyValue(MyClass)
        self.assertTrue(hasattr(lazy._ensure(), "value"))
        del lazy.value
        self.assertFalse(hasattr(lazy._ensure(), "value"))

    def test_dir(self):
        """Test dir() on LazyValue"""
        lazy: LazyValue[str] = LazyValue(lambda: "hello")
        dir_result = dir(lazy)
        self.assertIn("upper", dir_result)
        self.assertIn("lower", dir_result)


class TestLazyValueContainers(unittest.TestCase):
    """Test container operations"""

    def test_getitem_list(self):
        """Test indexing on list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3, 4, 5])
        self.assertEqual(lazy[0], 1)
        self.assertEqual(lazy[2], 3)
        self.assertEqual(lazy[-1], 5)

    def test_setitem_list(self):
        """Test setting items in list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3])
        lazy[1] = 99
        self.assertEqual(lazy[1], 99)

    def test_delitem_list(self):
        """Test deleting items from list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3])
        del lazy[1]
        self.assertEqual(lazy(), [1, 3])

    def test_getitem_dict(self):
        """Test getting items from dict"""
        lazy: LazyValue[dict[str, int]] = LazyValue(lambda: {"a": 1, "b": 2})
        self.assertEqual(lazy["a"], 1)
        self.assertEqual(lazy["b"], 2)

    def test_delitem_dict(self):
        """Test deleting items from dict"""
        lazy: LazyValue[dict[str, int]] = LazyValue(lambda: {"a": 1, "b": 2})
        del lazy["a"]
        self.assertNotIn("a", lazy())
        self.assertIn("b", lazy())

    def test_iter_list(self):
        """Test iteration over list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3])
        result = list(lazy)
        self.assertEqual(result, [1, 2, 3])

    def test_iter_dict(self):
        """Test iteration over dict"""
        lazy: LazyValue[dict[str, int]] = LazyValue(lambda: {"a": 1, "b": 2})
        result = list(lazy)
        self.assertIn("a", result)
        self.assertIn("b", result)

    def test_len_list(self):
        """Test len() on list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3, 4, 5])
        self.assertEqual(len(lazy), 5)

    def test_len_dict(self):
        """Test len() on dict"""
        lazy: LazyValue[dict[str, int]] = LazyValue(lambda: {"a": 1, "b": 2})
        self.assertEqual(len(lazy), 2)

    def test_contains_list(self):
        """Test 'in' operator on list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [1, 2, 3])
        self.assertIn(2, lazy)
        self.assertNotIn(5, lazy)

    def test_contains_dict(self):
        """Test 'in' operator on dict"""
        lazy: LazyValue[dict[str, int]] = LazyValue(lambda: {"a": 1, "b": 2})
        self.assertIn("a", lazy)
        self.assertNotIn("c", lazy)


class TestLazyValueCallable(unittest.TestCase):
    """Test callable functionality"""

    def test_call_no_args_returns_value(self):
        """Test calling with no args returns the value"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        self.assertEqual(lazy(), 42)

    def test_call_callable_value_with_args(self):
        """Test calling when underlying value is callable"""

        def add(a: int, b: int) -> int:
            return a + b

        lazy: LazyValue = LazyValue(lambda: add)
        result = lazy(5, 3)
        self.assertEqual(result, 8)

    def test_call_callable_value_with_kwargs(self):
        """Test calling with keyword arguments"""

        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        lazy: LazyValue = LazyValue(lambda: greet)
        result = lazy("World", greeting="Hi")
        self.assertEqual(result, "Hi, World!")

    def test_call_non_callable_with_args_raises(self):
        """Test calling non-callable value with args raises TypeError"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        with self.assertRaises(TypeError) as context:
            lazy(1, 2)
        self.assertIn("not callable", str(context.exception))


class TestLazyValueEquality(unittest.TestCase):
    """Test equality operations"""

    def test_eq_with_value(self):
        """Test equality with direct value"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        self.assertEqual(lazy, 42)
        self.assertNotEqual(lazy, 43)

    def test_eq_with_another_lazy(self):
        """Test equality with another LazyValue"""
        lazy1: LazyValue[int] = LazyValue(lambda: 42)
        lazy2: LazyValue[int] = LazyValue(lambda: 42)
        lazy3: LazyValue[int] = LazyValue(lambda: 43)
        self.assertEqual(lazy1, lazy2)
        self.assertNotEqual(lazy1, lazy3)

    def test_ne(self):
        """Test inequality operator"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)
        self.assertTrue(lazy != 43)
        self.assertFalse(lazy != 42)


class TestLazyValueContextManager(unittest.TestCase):
    """Test context manager delegation"""

    def test_context_manager_with_file(self):
        """Test using LazyValue with context manager (file-like object)"""
        import io

        lazy: LazyValue[io.StringIO] = LazyValue(lambda: io.StringIO("test content"))

        with lazy as f:
            content = f.read()
            self.assertEqual(content, "test content")

    def test_context_manager_without_support(self):
        """Test context manager with non-context-manager value"""
        lazy: LazyValue[int] = LazyValue(lambda: 42)

        # Should not raise, just returns the value
        with lazy as value:
            self.assertEqual(value, 42)


class TestLazyValueCustomClass(unittest.TestCase):
    """Test LazyValue with custom classes"""

    def test_custom_class(self):
        """Test LazyValue with custom class"""

        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

            def greet(self) -> str:
                return f"Hello, I'm {self.name}"

        lazy: LazyValue[Person] = LazyValue(lambda: Person("Alice", 30))

        # Test attribute access
        self.assertEqual(lazy.name, "Alice")
        self.assertEqual(lazy.age, 30)

        # Test method call
        self.assertEqual(lazy.greet(), "Hello, I'm Alice")

        # Test attribute modification
        lazy.age = 31
        self.assertEqual(lazy.age, 31)


class TestLazyValueEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_exception_in_getter(self):
        """Test that exceptions in getter are propagated"""

        def failing_getter():
            raise ValueError("Something went wrong")

        lazy: LazyValue[int] = LazyValue(failing_getter)

        with self.assertRaises(ValueError) as context:
            lazy()
        self.assertIn("Something went wrong", str(context.exception))

    def test_none_value(self):
        """Test LazyValue with None value"""
        lazy: LazyValue[None] = LazyValue(lambda: None)
        self.assertIsNone(lazy())
        self.assertFalse(bool(lazy))

    def test_empty_list(self):
        """Test LazyValue with empty list"""
        lazy: LazyValue[list[int]] = LazyValue(lambda: [])
        self.assertEqual(len(lazy), 0)
        self.assertFalse(bool(lazy))

    def test_complex_nested_structure(self):
        """Test LazyValue with complex nested structure"""
        data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], "count": 2}
        lazy: LazyValue[dict] = LazyValue(lambda: data)

        self.assertEqual(lazy["count"], 2)
        self.assertEqual(lazy["users"][0]["name"], "Alice")
        self.assertEqual(len(lazy["users"]), 2)


if __name__ == "__main__":
    unittest.main()

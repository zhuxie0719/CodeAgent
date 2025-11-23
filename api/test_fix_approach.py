# Test that demonstrates the fix approach
class TestState:
    def __init__(self):
        self._preserved_exc = None

class TestContext:
    def __init__(self):
        self._state = TestState()
    
    @property
    def preserved_exc(self):
        """Get the preserved exception."""
        return self._state._preserved_exc

    @preserved_exc.setter
    def preserved_exc(self, value):
        """Set the preserved exception."""
        self._state._preserved_exc = value

# Test the fix
ctx = TestContext()
ctx.preserved_exc = "test_exception"
print(f"SUCCESS: preserved_exc property works: {ctx.preserved_exc}")

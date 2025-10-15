import collections
import pickle
import unittest


class FrozenDictTests(unittest.TestCase):

    def test_constructor_and_lookup(self):
        fd = frozendict({'a': 1}, b=2)
        self.assertEqual(fd['a'], 1)
        self.assertEqual(fd['b'], 2)
        self.assertEqual(len(fd), 2)
        self.assertEqual(set(fd.items()), {('a', 1), ('b', 2)})

    def test_constructor_identity(self):
        fd = frozendict({'a': 1})
        self.assertIs(frozendict(fd), fd)
        self.assertIs(frozendict.__new__(frozendict, fd), fd)

    def test_constructor_does_not_share_storage(self):
        source = {'a': 1}
        fd = frozendict(source)
        source['b'] = 2
        self.assertEqual(dict(fd), {'a': 1})

    def test_invalid_kwargs_type(self):
        with self.assertRaises(TypeError):
            frozendict({}, **{1: 2})

    def test_is_mapping(self):
        fd = frozendict(a=1)
        self.assertIsInstance(fd, collections.abc.Mapping)
        self.assertTrue('a' in fd)
        self.assertEqual(list(fd), ['a'])

    def test_equality_and_hash(self):
        lhs = frozendict({'x': 1, 'y': 2})
        rhs = frozendict({'y': 2, 'x': 1})
        self.assertEqual(lhs, rhs)
        self.assertEqual(lhs, {'x': 1, 'y': 2})
        self.assertEqual(hash(lhs), hash(rhs))

    def test_hash_lazy_and_cached(self):
        class CountingInt(int):
            hash_calls = 0
            def __hash__(self):
                type(self).hash_calls += 1
                return super().__hash__()

        payload = {CountingInt(1): CountingInt(10), CountingInt(2): CountingInt(20)}
        CountingInt.hash_calls = 0
        fd = frozendict(payload)
        # Hash not computed during construction
        self.assertEqual(CountingInt.hash_calls, 0)

        # First hash() call computes it
        h1 = hash(fd)
        first_calls = CountingInt.hash_calls
        self.assertGreater(first_calls, 0)

        # Second hash() call uses cached value
        h2 = hash(fd)
        self.assertEqual(CountingInt.hash_calls, first_calls)
        self.assertEqual(h1, h2)

    def test_conditionally_hashable(self):
        # Hashable values → hashable frozendict
        fd1 = frozendict({'a': 1, 'b': 'x', 'c': (1, 2)})
        self.assertIsInstance(hash(fd1), int)

        # Unhashable values → unhashable frozendict
        fd2 = frozendict({'a': [], 'b': 2})
        with self.assertRaises(TypeError) as cm:
            hash(fd2)
        self.assertIn('unhashable', str(cm.exception).lower())

        # But can still use unhashable frozendict
        self.assertEqual(fd2['a'], [])
        self.assertEqual(fd2['b'], 2)
        self.assertEqual(len(fd2), 2)

        # Nested unhashable
        fd3 = frozendict({'x': frozendict({'y': []})})
        with self.assertRaises(TypeError):
            hash(fd3)

    def test_hash_collision_fix(self):
        # These used to collide due to weak key-value combining
        fd1 = frozendict({'a': 'a', 'b': 1})
        fd2 = frozendict({'a': 'a', 'b': 'b'})
        self.assertNotEqual(hash(fd1), hash(fd2))

        # More collision tests
        fd3 = frozendict({'x': 1, 'y': 2})
        fd4 = frozendict({'x': 2, 'y': 1})
        self.assertNotEqual(hash(fd3), hash(fd4))

    def test_pickle_roundtrip(self):
        fd = frozendict({'a': 1, 'b': 2})
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            restored = pickle.loads(pickle.dumps(fd, proto))
            self.assertIsInstance(restored, frozendict)
            self.assertEqual(restored, fd)


if __name__ == '__main__':
    unittest.main()

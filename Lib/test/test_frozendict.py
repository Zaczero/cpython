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

    def test_requires_hashable_values(self):
        with self.assertRaises(TypeError):
            frozendict({'a': []})

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

    def test_hash_precomputed(self):
        class CountingInt(int):
            hash_calls = 0
            def __hash__(self):
                type(self).hash_calls += 1
                return super().__hash__()

        payload = {CountingInt(1): 1, CountingInt(2): 2}
        CountingInt.hash_calls = 0
        fd = frozendict(payload)
        self.assertEqual(CountingInt.hash_calls, len(payload))
        CountingInt.hash_calls = 0
        hash(fd)
        self.assertEqual(CountingInt.hash_calls, 0)

    def test_pickle_roundtrip(self):
        fd = frozendict({'a': 1, 'b': 2})
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            restored = pickle.loads(pickle.dumps(fd, proto))
            self.assertIsInstance(restored, frozendict)
            self.assertEqual(restored, fd)


if __name__ == '__main__':
    unittest.main()

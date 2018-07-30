from multipledispatch.conflict import (supercedes, ordering, ambiguities,
        ambiguous, super_signature, consistent)
from multipledispatch.dispatcher import Variadic


class A(object): pass
class B(A): pass
class C(object): pass


def test_supercedes():
    assert supercedes([B], [A])
    assert supercedes([B, A], [A, A])
    assert not supercedes([B, A], [A, B])
    assert not supercedes([A], [B])


def test_consistent():
    assert consistent([A], [A])
    assert consistent([B], [B])
    assert not consistent([A], [C])
    assert consistent([A, B], [A, B])
    assert consistent([B, A], [A, B])
    assert not consistent([B, A], [B])
    assert not consistent([B, A], [B, C])


def test_super_signature():
    assert super_signature([[A]]) == [A]
    assert super_signature([[A], [B]]) == [B]
    assert super_signature([[A, B], [B, A]]) == [B, B]
    assert super_signature([[A, A, B], [A, B, A], [B, A, A]]) == [B, B, B]


def test_ambiguous():
    assert not ambiguous([A], [A])
    assert not ambiguous([A], [B])
    assert not ambiguous([B], [B])
    assert not ambiguous([A, B], [B, B])
    assert ambiguous([A, B], [B, A])


def test_ambiguities():
    signatures = [[A], [B], [A, B], [B, A], [A, C]]
    expected = set([((A, B), (B, A))])
    result = ambiguities(signatures)
    assert set(map(frozenset, expected)) == set(map(frozenset, result))

    signatures = [[A], [B], [A, B], [B, A], [A, C], [B, B]]
    expected = set()
    result = ambiguities(signatures)
    assert set(map(frozenset, expected)) == set(map(frozenset, result))


def test_ordering():
    signatures = [[A, A], [A, B], [B, A], [B, B], [A, C]]
    ord = ordering(signatures)
    assert ord[0] == (B, B) or ord[0] == (A, C)
    assert ord[-1] == (A, A) or ord[-1] == (A, C)


def test_type_mro():
    assert super_signature([[object], [type]]) == [type]


def test_supercedes_variadic():
    assert supercedes((Variadic[B],), (Variadic[A],))
    assert supercedes((B, Variadic[A]), (Variadic[A],))
    assert supercedes((Variadic[A],), (Variadic[(A, C)],))
    assert supercedes((A, B, Variadic[C]), (Variadic[object],))
    assert supercedes((A, Variadic[B]), (Variadic[A],))
    assert supercedes(tuple([]), (Variadic[A],))
    assert supercedes((A, A, A), (A, Variadic[A]))
    assert not supercedes((Variadic[A],), (Variadic[B],))
    assert not supercedes((Variadic[A],), (B, Variadic[A]))
    assert not supercedes((Variadic[(A, C)],), (Variadic[A],))
    assert not supercedes((Variadic[object],), (A, B, Variadic[C]))
    assert not supercedes((Variadic[A],), (A, Variadic[B]))
    assert not supercedes((Variadic[A],), tuple([]))
    assert not supercedes((A, Variadic[A]), (A, A, A))


def test_consistent_variadic():
    # basic check
    assert consistent((Variadic[A],), (Variadic[A],))
    assert consistent((Variadic[B],), (Variadic[B],))
    assert not consistent((Variadic[C],), (Variadic[A],))

    # union types
    assert consistent((Variadic[(A, C)],), (Variadic[A],))
    assert consistent((Variadic[(A, C)],), (Variadic[(C, A)],))
    assert consistent((Variadic[(A, B, C)],), (Variadic[(C, B, A)],))
    assert consistent((A, B, C), (Variadic[(A, B, C)],))
    assert consistent((A, B, C), (A, Variadic[(B, C)]))

    # more complex examples
    assert consistent(tuple([]), (Variadic[object],))
    assert consistent((A, A, B), (A, A, Variadic[B]))
    assert consistent((A, A, B), (A, A, Variadic[A]))
    assert consistent((A, B, Variadic[C]), (B, A, Variadic[C]))
    assert consistent((A, B, Variadic[C]), (B, A, Variadic[(C, B)]))

    # not consistent
    assert not consistent((C,), (Variadic[A],))
    assert not consistent((A, A, Variadic[C]), (A, Variadic[C]))
    assert not consistent((A, B, Variadic[C]), (C, B, Variadic[C]))

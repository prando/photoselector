from photoselector.prefetch.window import plan_for


def test_plan_for_index_10_of_30() -> None:
    plan = plan_for(10, 30)
    assert plan.p0 == frozenset({10})
    assert 9 in plan.p1 and 14 in plan.p1
    assert 6 in plan.p1
    assert 5 in plan.p2 and 22 in plan.p2
    assert 10 not in plan.p1
    old = plan_for(0, 30)
    assert 0 in old.p0
    assert not old.contains(20)

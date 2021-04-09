import pytest


def test_add_parallel_axis(simulation_builder):
    simulation_builder.add_parallel_axis({})

    result = simulation_builder.axes

    assert result == [[{}]]


def test_add_parallel_axes(simulation_builder):
    simulation_builder.add_parallel_axis({})
    simulation_builder.add_parallel_axis({})

    result = simulation_builder.axes

    assert result == [[{}, {}]]


def test_add_perpendicular_axes(simulation_builder):
    simulation_builder.add_perpendicular_axis({})
    simulation_builder.add_perpendicular_axis({})

    result = simulation_builder.axes

    assert result == [[], [{}], [{}]]


def test_expand_axis_on_persons(simulation_builder, persons, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}})
    simulation_builder.register_variable('salary', persons)
    simulation_builder.add_parallel_axis({'count': 3, 'name': 'salary', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.expand_axes()
    assert simulation_builder.get_input('salary', month) == pytest.approx([0, 1500, 3000])
    assert simulation_builder.get_count('persons') == 3
    assert simulation_builder.get_ids('persons') == ['Alicia0', 'Alicia1', 'Alicia2']


def test_expand_axis_without_period(simulation_builder, persons, month):
    simulation_builder.set_default_period(month)
    simulation_builder.add_person_entity(persons, {'Alicia': {}})
    simulation_builder.register_variable('salary', persons)
    simulation_builder.add_parallel_axis({'count': 3, 'name': 'salary', 'min': 0, 'max': 3000})
    simulation_builder.expand_axes()
    assert simulation_builder.get_input('salary', month) == pytest.approx([0, 1500, 3000])


def test_expand_two_axes(simulation_builder, persons, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}})
    simulation_builder.register_variable('salary', persons)
    simulation_builder.add_parallel_axis({'count': 3, 'name': 'salary', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.add_parallel_axis({'count': 3, 'name': 'pension', 'min': 0, 'max': 2000, 'period': month})
    simulation_builder.expand_axes()
    assert simulation_builder.get_input('salary', month) == pytest.approx([0, 1500, 3000])
    assert simulation_builder.get_input('pension', month) == pytest.approx([0, 1000, 2000])


def test_expand_axis_with_group(simulation_builder, persons, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}})
    simulation_builder.register_variable('salary', persons)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'salary', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'salary', 'min': 0, 'max': 3000, 'period': month, 'index': 1})
    simulation_builder.expand_axes()
    assert simulation_builder.get_count('persons') == 4
    assert simulation_builder.get_ids('persons') == ['Alicia0', 'Javier1', 'Alicia2', 'Javier3']
    assert simulation_builder.get_input('salary', month) == pytest.approx([0, 0, 3000, 3000])


def test_expand_axis_with_group_int_period(simulation_builder, persons, year):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}})
    simulation_builder.register_variable('salary', persons)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'salary', 'min': 0, 'max': 3000, 'period': int(year)})
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'salary', 'min': 0, 'max': 3000, 'period': int(year), 'index': 1})
    simulation_builder.expand_axes()
    assert simulation_builder.get_input('salary', str(year)) == pytest.approx([0, 0, 3000, 3000])


def test_expand_axis_on_group_entity(simulation_builder, persons, households, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}, 'Tom': {}})
    simulation_builder.add_group_entity('persons', ['Alicia', 'Javier', 'Tom'], households, {
        'housea': {'parents': ['Alicia', 'Javier']},
        'houseb': {'parents': ['Tom']},
        })
    simulation_builder.register_variable('rent', households)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'rent', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.expand_axes()
    assert simulation_builder.get_count('households') == 4
    assert simulation_builder.get_ids('households') == ['housea0', 'houseb1', 'housea2', 'houseb3']
    assert simulation_builder.get_input('rent', month) == pytest.approx([0, 0, 3000, 0])


def test_axis_on_group_expands_persons(simulation_builder, persons, households, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}, 'Tom': {}})
    simulation_builder.add_group_entity('persons', ['Alicia', 'Javier', 'Tom'], households, {
        'housea': {'parents': ['Alicia', 'Javier']},
        'houseb': {'parents': ['Tom']},
        })
    simulation_builder.register_variable('rent', households)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'rent', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.expand_axes()
    assert simulation_builder.get_count('persons') == 6


def test_expand_axis_distributes_roles(simulation_builder, persons, households, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}, 'Tom': {}})
    simulation_builder.add_group_entity('persons', ['Alicia', 'Javier', 'Tom'], households, {
        'housea': {'parents': ['Alicia']},
        'houseb': {'parents': ['Tom'], 'children': ['Javier']},
        })
    simulation_builder.register_variable('rent', households)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'rent', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.expand_axes()
    assert [role.key for role in simulation_builder.get_roles('households')] == ['parent', 'child', 'parent', 'parent', 'child', 'parent']


def test_expand_axis_on_persons_distributes_roles(simulation_builder, persons, households, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}, 'Tom': {}})
    simulation_builder.add_group_entity('persons', ['Alicia', 'Javier', 'Tom'], households, {
        'housea': {'parents': ['Alicia']},
        'houseb': {'parents': ['Tom'], 'children': ['Javier']},
        })
    simulation_builder.register_variable('salary', persons)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'salary', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.expand_axes()
    assert [role.key for role in simulation_builder.get_roles('households')] == ['parent', 'child', 'parent', 'parent', 'child', 'parent']


def test_expand_axis_distributes_memberships(simulation_builder, persons, households, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}, 'Javier': {}, 'Tom': {}})
    simulation_builder.add_group_entity('persons', ['Alicia', 'Javier', 'Tom'], households, {
        'housea': {'parents': ['Alicia']},
        'houseb': {'parents': ['Tom'], 'children': ['Javier']},
        })
    simulation_builder.register_variable('rent', households)
    simulation_builder.add_parallel_axis({'count': 2, 'name': 'rent', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.expand_axes()
    assert simulation_builder.get_memberships('households') == [0, 1, 1, 2, 3, 3]


def test_expand_perpendicular_axes(simulation_builder, persons, month):
    simulation_builder.add_person_entity(persons, {'Alicia': {}})
    simulation_builder.register_variable('salary', persons)
    simulation_builder.register_variable('pension', persons)
    simulation_builder.add_parallel_axis({'count': 3, 'name': 'salary', 'min': 0, 'max': 3000, 'period': month})
    simulation_builder.add_perpendicular_axis({'count': 2, 'name': 'pension', 'min': 0, 'max': 2000, 'period': month})
    simulation_builder.expand_axes()
    assert simulation_builder.get_input('salary', month) == pytest.approx([0, 1500, 3000, 0, 1500, 3000])
    assert simulation_builder.get_input('pension', month) == pytest.approx([0, 0, 0, 2000, 2000, 2000])

# Integration test


def test_simulation_with_axes(simulation_builder, tax_benefit_system, axes, month):
    simulation = simulation_builder.build_from_dict(tax_benefit_system, axes)
    assert simulation.get_array('salary', month) == pytest.approx([0, 0, 0, 0, 0, 0])
    assert simulation.get_array('rent', month) == pytest.approx([0, 0, 3000, 0])

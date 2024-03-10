import pytest
from django.shortcuts import reverse
from topobank.manager.models import Surface, Topography
from topobank.manager.tests.utils import (SurfaceFactory, TagFactory,
                                          Topography1DFactory,
                                          Topography2DFactory, UserFactory)

from ..utils import (current_selection_as_surface_list, instances_to_selection,
                     instances_to_surfaces, instances_to_topographies,
                     selection_to_instances, tags_for_user)


@pytest.fixture
def mock_topos(mocker):
    mocker.patch('topobank.manager.models.Topography', autospec=True)
    mocker.patch('topobank.manager.models.Surface', autospec=True)
    mocker.patch('topobank.manager.models.Tag', autospec=True)


@pytest.fixture
def testuser(django_user_model):
    username = 'testuser'
    user, created = django_user_model.objects.get_or_create(username=username)
    return user


@pytest.mark.skip('Mocking does not seem to work properly here')
def test_selection_to_instances(testuser, mock_topos):
    from topobank.manager.models import Surface, Tag, Topography

    selection = ('topography-1', 'topography-2', 'surface-1', 'surface-3', 'tag-1', 'tag-2', 'tag-4')
    selection_to_instances(selection)

    Topography.objects.filter.assert_called_with(id__in={1, 2})
    Surface.objects.filter.assert_called_with(id__in={1, 3})  # set instead of list
    Tag.objects.filter.assert_called_with(id__in={1, 2, 4})  # set instead of list


@pytest.mark.django_db
def test_instances_to_selection():
    user = UserFactory()

    tag1 = TagFactory()
    tag2 = TagFactory()

    surface1 = SurfaceFactory(creator=user, tags=[tag1, tag2])
    surface2 = SurfaceFactory(creator=user)

    topo1 = Topography2DFactory(surface=surface1)
    topo2 = Topography1DFactory(surface=surface2, tags=[tag2])

    assert topo1.surface != topo2.surface

    s = instances_to_selection(topographies=[topo1, topo2])

    assert s == [f'topography-{topo1.id}', f'topography-{topo2.id}']

    #
    # It should be possible to give surfaces
    #
    s = instances_to_selection(surfaces=[surface1, surface2])
    assert s == [f'surface-{surface1.id}', f'surface-{surface2.id}']

    #
    # It should be possible to give surfaces and topographies
    #
    s = instances_to_selection(topographies=[topo1], surfaces=[surface2])
    assert s == [f'surface-{surface2.id}', f'topography-{topo1.id}']

    #
    # It should be possible to pass tags
    #
    s = instances_to_selection(tags=[tag2, tag1])
    assert s == [f'tag-{tag1.id}', f'tag-{tag2.id}']

    # Also mixed with other instances
    s = instances_to_selection(tags=[tag2, tag1], topographies=[topo1], surfaces=[surface2])
    assert s == [f'surface-{surface2.id}', f'tag-{tag1.id}', f'tag-{tag2.id}', f'topography-{topo1.id}']


@pytest.mark.django_db
def test_tags_for_user(two_topos):
    topo1 = Topography.objects.get(name="Example 3 - ZSensor")
    topo1.tags = ['rough', 'projects/a']
    topo1.save()

    from topobank.manager.models import Tag
    print("Tags of topo1:", topo1.tags)
    print(Tag.objects.all())

    topo2 = Topography.objects.get(name="Example 4 - Default")
    topo2.tags = ['interesting']
    topo2.save()

    surface1 = Surface.objects.get(name="Surface 1")
    surface1.tags = ['projects/C', 'rare']
    surface1.save()

    surface2 = Surface.objects.get(name="Surface 2")
    surface2.tags = ['projects/B', 'a long tag with spaces']
    surface2.save()

    user = surface1.creator

    assert surface2.creator == user

    tags = tags_for_user(user)

    assert set(t.name for t in tags) == {'a long tag with spaces', 'interesting', 'rare', 'rough',
                                         'projects/a', 'projects/b', 'projects/c', 'projects'}


@pytest.mark.django_db
def test_instances_to_topographies(user_three_topographies_three_surfaces_three_tags):
    #
    # Define instances as local variables
    #
    user, (topo1a, topo1b, topo2a), (surface1, surface2, surface3), (tag1, tag2, tag3) \
        = user_three_topographies_three_surfaces_three_tags

    # nothing given, nothing returned
    assert list(instances_to_topographies([], [], [])) == []

    # surface without topographies is the same
    assert list(instances_to_topographies([], [surface3], [])) == []

    # only one surface given
    assert list(instances_to_topographies([], [surface1], [])) == [topo1a, topo1b]

    # only two surfaces given
    assert list(instances_to_topographies([], [surface2, surface1], [])) == [topo1a, topo1b, topo2a]

    # an empty surface makes no difference here
    assert list(instances_to_topographies([], [surface2, surface1, surface3], [])) == [topo1a, topo1b, topo2a]

    # an additional topography makes no difference
    assert list(instances_to_topographies([topo1a], [surface1], [])) == [topo1a, topo1b]

    # also single topographies can be selected
    assert list(instances_to_topographies([topo2a, topo1b], [], [])) == [topo1b, topo2a]

    # a single tag can be selected
    assert list(instances_to_topographies([], [], [tag3])) == [topo1b]

    # an additional topography given does not change result if already tagged the same way
    assert list(instances_to_topographies([topo1b], [], [tag3])) == [topo1b]

    # also two tags can be given
    assert list(instances_to_topographies([], [], [tag2, tag3])) == [topo1b, topo2a]


@pytest.mark.django_db
def test_instances_to_surfaces(user_three_topographies_three_surfaces_three_tags):
    #
    # Define instances as local variables
    #
    user, (topo1a, topo1b, topo2a), (surface1, surface2, surface3), (tag1, tag2, tag3) \
        = user_three_topographies_three_surfaces_three_tags

    # nothing given, nothing returned
    assert list(instances_to_surfaces([], [])) == []

    # surface without topographies is the same
    assert list(instances_to_surfaces([surface3], [])) == [surface3]

    # two surfaces given
    assert list(instances_to_surfaces([surface2, surface1], [])) == [surface1, surface2]

    # a single tag can be selected
    assert list(instances_to_surfaces([], [tag3])) == [surface3]

    # also two tags can be given
    assert list(instances_to_surfaces([], [tag2, tag3])) == [surface2, surface3]


@pytest.mark.django_db
def test_related_surfaces_for_selection(rf):
    user = UserFactory()

    # create tags
    tag1 = TagFactory(name='apple')
    tag2 = TagFactory(name='banana')

    # create surfaces
    surf1 = SurfaceFactory(creator=user, tags=[tag1])
    surf2 = SurfaceFactory(creator=user)
    surf3 = SurfaceFactory(creator=user, tags=[tag1])

    # add some topographies
    topo1a = Topography1DFactory(surface=surf1)
    Topography2DFactory(surface=surf1, tags=[tag2])
    Topography2DFactory(surface=surf2, tags=[tag1])

    # surf3 has no topography

    def get_request(topographies=[], surfaces=[], tags=[]):
        """Simple get request while setting the selection"""
        request = rf.get(reverse('ce_ui:select'))
        request.user = user
        request.session = {'selection': instances_to_selection(
            topographies=topographies,
            surfaces=surfaces,
            tags=tags,
        )}
        return request

    # tag 'apple' should return all three surfaces
    assert current_selection_as_surface_list(get_request(tags=[tag1])) == [surf1, surf2, surf3]

    # one topography should return its surface
    assert current_selection_as_surface_list(get_request(topographies=[topo1a])) == [surf1]

    # We should be able to mix tags, topographies and surfaces
    assert current_selection_as_surface_list(get_request(topographies=[topo1a],
                                                         surfaces=[surf1],
                                                         tags=[tag2])) == [surf1]

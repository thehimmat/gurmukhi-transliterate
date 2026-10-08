"""Story tags: ``@pytest.mark.story('US-007')`` links a test to user-stories/US-007-*.md.

``pytest --story US-007`` runs only that story's acceptance tests.
"""


def pytest_addoption(parser):
    parser.addoption('--story', action='append', default=[], metavar='US-NNN',
                     help='run only tests tagged with this user story (repeatable)')


def pytest_configure(config):
    config.addinivalue_line('markers', 'story(*ids): acceptance test for these user stories')


def pytest_collection_modifyitems(config, items):
    wanted = set(config.getoption('story'))
    if not wanted:
        return
    keep, drop = [], []
    for item in items:
        ids = {i for m in item.iter_markers('story') for i in m.args}
        (keep if ids & wanted else drop).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep

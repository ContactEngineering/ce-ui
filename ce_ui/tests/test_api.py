from django.urls import reverse

def test_api():
    """Test API routes"""
    assert reverse('ce_ui:results-detail', kwargs=dict(pk=123)) == '/analysis/html/detail/123/'
    assert reverse('ce_ui:results-list') == '/analysis/html/list/'

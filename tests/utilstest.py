def list_equal(l1, l2):
    l1.sort()
    l2.sort()
    return l1==l2

def check_attribute_on_channel(vis, attr_name, channelName):
	assert vis.get_attr_by_channel(channelName)[0].attribute == attr_name

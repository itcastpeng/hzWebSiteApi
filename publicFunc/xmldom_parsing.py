
def xmldom(collection, data):
    data_dict = {}
    for i in data:
        data_dict['{}'.format(i)] = collection.getElementsByTagName("{}".format(i))[0].childNodes[0].data
        # print('data_dict----> ',data_dict)
    return data_dict

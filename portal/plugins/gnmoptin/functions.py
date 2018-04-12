from models import UserOptIn


def userfeature(user, feature):
    features = {}
    for item in UserOptIn.objects.filter(user=user):
        features[item.feature] = item.enabled

    if feature in features:
        return features[feature]
    else:
        return 'None'

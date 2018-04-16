from models import UserOptIn


def userfeature(user, feature):
    count=0
    for item in UserOptIn.objects.filter(user=user, feature=feature):
        count+=1

    if count>0:
        return True
    else:
        return False

from .auth import get


def auth_functions():
    return dict(
        acitvity_list=get.vic_activity_list,
        package_activity_list=get.vic_package_activity_list
    )

class UserNotFoundError(Exception):
    pass


class IncorrectUserInformationError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


class BusinessError(Exception):
    pass


class ForbiddenAccountAccess(Exception):
    pass
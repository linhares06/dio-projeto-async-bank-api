from databases.interfaces import Record

from src.database import database
from src.models.transaction import transactions, TransactionType
from src.models.account import accounts
from src.schemas.transaction import TransactionIn
from src.schemas.user import Role
from src.exceptions import AccountNotFoundError, BusinessError, ForbiddenAccountAccess
from src.services.account import AccountService


class TransactionService:
    async def create(self, transaction: TransactionIn) -> int:
        """
        Creates a new transaction and updates the associated account's balance.

        Args:
            transaction (TransactionIn): The transaction details, including type, amount, and account ID.

        Returns:
            int: The ID of the newly created transaction.

        Raises:
            AccountNotFoundError: If the account specified in the transaction does not exist.
            BusinessError: If the transaction is a withdrawal and the account's balance is insufficient.
        """
        query = accounts.select().where(accounts.c.id == transaction.account_id)
        account = await database.fetch_one(query)
        if not account:
            raise AccountNotFoundError

        if transaction.type == TransactionType.WITHDRAWAL:
            balance = float(account.balance) - transaction.amount
            if balance < 0:
                raise BusinessError
        else:
            balance = float(account.balance) + transaction.amount

        # Create transaction entry
        transaction_id = await self.__register_transaction(transaction)
        # Update account balance
        await self.__update_account_balance(transaction.account_id, balance)

        query = transactions.select().where(transactions.c.id == transaction_id)
        
        return await database.fetch_one(query)

    async def read_all_by_account_id(self, account_id: int, current_user: dict[str, str], limit: int, skip: int, ) -> list[Record]:
        """
        Retrieves all transactions for a given account, with pagination, 
        while enforcing user permissions.

        Args:
            account_id (int): The ID of the account whose transactions are to be retrieved.
            current_user (dict[str, str]): Information about the current user, including their role and ID.
            limit (int): The maximum number of transactions to retrieve.
            skip (int): The number of transactions to skip (for pagination).

        Returns:
            list[Record]: A list of transactions associated with the given account.

        Raises:
            AccountNotFoundError: If the account with the given ID does not exist.
            ForbiddenAccountAccess: If the current user does not have permission to access the transaction.
        """
        total = await AccountService.count(account_id)
        if not total:
            raise AccountNotFoundError
        
        # Ensure only authorized users can access the account:
        # Managers have unrestricted access; non-managers can only access their own accounts.
        if current_user.get("role", "") != Role.MANAGER:
            user_account_id = await self.__get_user_id_by_account_id(account_id)
            if user_account_id != int(current_user.get("user_id", "")):
                raise ForbiddenAccountAccess
        
        query = transactions.select().where(transactions.c.account_id == account_id).limit(limit).offset(skip)

        return await database.fetch_all(query)
       
    async def __update_account_balance(self, account_id: int, balance: float) -> None:
        command = accounts.update().where(accounts.c.id == account_id).values(balance=balance)
        await database.execute(command)

    async def __register_transaction(self, transaction: TransactionIn) -> int:
        command = transactions.insert().values(
            account_id=transaction.account_id,
            type=transaction.type,
            amount=transaction.amount,
        )
        return await database.execute(command)

    async def __get_user_id_by_account_id(self, account_id: int) -> int:
        query = accounts.select().where(accounts.c.id == account_id)
        account = await database.fetch_one(query)
        if not account:
            raise AccountNotFoundError

        return account.user_id
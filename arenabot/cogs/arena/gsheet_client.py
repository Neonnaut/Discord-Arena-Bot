import re
import gspread_asyncio
from google.oauth2.service_account import Credentials
from constants import GSHEETS_KEY
from discord import User

from gspread.cell import Cell

class Arena_Schema(gspread_asyncio.AsyncioGspreadClientManager):
    def __init__(self, workbook_key: str, sheet: str):
        super().__init__(self.get_creds)

        self.workbook_key = workbook_key
        self.sheet = sheet

    def get_creds(self):
        creds = Credentials.from_service_account_info(GSHEETS_KEY)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    async def get_sheet(self) -> gspread_asyncio.AsyncioGspreadSpreadsheet:
        """
        Returns a google sheet object
        """
        agc = await self.authorize()
        try:
            workbook = await agc.open_by_key(self.workbook_key)
        except:
            return None, "Unable to access the workbook."
        else:
            try:
                got_sheet = await workbook.worksheet(self.sheet)
            except:
                return None, f"Unable to access the sheet \"{self.sheet}\"."
            else:
                return got_sheet, "Got the sheet"

    async def set_combatant(
        self,
        user: User,
        cell_values: list,
    ) -> int:
        """
        This function sets a combatant
        """
        # Get the sheet
        sheet, message = await self.get_sheet()
        if not sheet:
            return None, message
        sheet: gspread_asyncio.AsyncioGspreadWorksheet

        field_headers = await sheet.row_values(1)
        if len(field_headers) <= 2:
            return None, "Error with the Google Sheet"
        key_header = field_headers.pop(0)

        # Get the combatant
        key_cell = await sheet.find(query=str(user.id), in_column=1)
        if key_cell is not None:

            ### Update the combatant cells

            # Cells to update
            cells = []
            finalised_fields = [] # header, value
            image = None

            # Create the list of cells to update
            for i in range(0, len(cell_values)):
                if cell_values[i] != None:
                    cells.append(Cell(row=key_cell.row, col=i+2, value=cell_values[i]))


                    finalised_fields.append(
                        f'{field_headers[i]}:`{cell_values[i]}`'
                    )
                    if field_headers[i] == "Image":
                        imageLink = re.findall('https?:\/\/.*\.(?:png|jpg|gif)', str(cell_values[i]))
                        if len(imageLink) != 0:
                            image = cell_values[i]

            # Update the cells of the row at the key
            if len(cells) != 0:
                try:
                    await sheet.update_cells(cells, value_input_option='USER_ENTERED')
                except Exception:
                    return None, "Error encountered"

        else:

            ### Append a new combatant
            sheet.append_row(cell_values, insert_data_option='USER_ENTERED')

        finalised_fields = finalised_fields[2:]
        # Format output as dict
        output = {
            'title': f'Username `{user.name}`, in sheet:`{sheet.title}`',
            'url': f'{sheet.url}',
            'fields': {
                f'Combatant: {cell_values[1]}': finalised_fields
            },
            'image': image
        }
        return output, "Updated your combatant."

    async def show_combatant(
        self,
        user: User,
    ) -> int:
        """
        This function is called on show_combatant
        """
        # Get the sheet
        sheet, message = await self.get_sheet()
        if not sheet:
            return None, message
        sheet: gspread_asyncio.AsyncioGspreadWorksheet

        combatant = None

        # First get all the field headers from the googlesheet, and the key header
        field_headers = await sheet.row_values(1)
        key_header = field_headers.pop(0)

        # Get the combatant
        key_cell = await sheet.find(query=str(user.id), in_column=1)
        if key_cell is None:
            return None, f"{user.name} does not have a combatant"
        combatant = await sheet.row_values(row=key_cell.row)
        combatant.pop(0)

        finalised_fields = []
        image = None
        for i in range(2, len(field_headers)):
            if field_headers[i] == "Image":
                imageLink = re.findall(
                    'https?:\/\/.*\.(?:png|jpg|gif)', str(combatant[i]))
                if len(imageLink) != 0:
                    image = combatant[i]
            else:
                try:
                    finalised_fields.append(f"{field_headers[i]}: `{combatant[i] or 'None'}`")
                except:
                    finalised_fields.append(f"{field_headers[i]}: `None`")
        
        # Format output as dict
        output = {
            'title': f'Username `{user.name}`, in sheet:`{sheet.title}`',
            'url': f'{sheet.url}',
            'fields': {
                f'Combatant: {combatant[1]}': finalised_fields
            },
            'image': image
        }
        return output, "Found combatant."

    async def get_combatants_for_arena_match(
        self,
        users: list[User],
    ) -> list:
        """
        Arena match
        This function iterates over a list of userIDs and gets their combatants
        """
        # Get the sheet
        sheet, message = await self.get_sheet()
        if not sheet:
            return None, message
        sheet: gspread_asyncio.AsyncioGspreadWorksheet

        combatants = []

        # Iterate and get all the combatants
        for user in users:
            key_cell = await sheet.find(query=str(user.id), in_column=1)
            if key_cell is None:
                return None, f"{user.name} has no combatant"
            combatants.append(await sheet.row_values(row=key_cell.row))

        return combatants, "Found all combatants"

    async def set_winner(self, userID):
        # Get the sheet
        sheet, message = await self.get_sheet()
        if not sheet:
            return None, message
        sheet: gspread_asyncio.AsyncioGspreadWorksheet


        key_cell = await sheet.find(query=str(userID), in_column=1)
        if key_cell is not None:
            try:
                old_win = await sheet.cell(row=key_cell.row, col=11)
                old_win = old_win.value
                await sheet.update_cell(key_cell.row, 11, int(old_win) + 1)
            except:
                pass

    


            
 
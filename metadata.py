import pandas as pd
def getmetadata(tables, driver):
        # -----------------------------------------------------
    # Getting the meta data in a csv file
    # -----------------------------------------------------
    # Find all tables

    if not tables:
        print("No table found.")
        driver.quit()
        exit()

    print("Tables found:", len(tables))

    for i, table in enumerate(tables):

        print("\n==============================")
        print("TABLE", i)
        print("==============================")

        headers = [
            th.get_text(" ", strip=True)
            for th in table.find_all("th")
        ]

        print("Headers:")
        print(headers)
    
    target_table = tables[2]  # Assuming the third table contains the desired data

    #df = pd.read_html(str(tables[2]))
# -------------------------------------------------------
# Extract headers
# -------------------------------------------------------

    header_row = target_table.find("tr")

    headers = []

    for cell in header_row.find_all(["th", "td"]):

        text = cell.get_text(
            " ",
            strip=True
        )

        headers.append(text)


    print("\nHEADERS:")
    print(headers)


    # -------------------------------------------------------
    # Extract rows
    # -------------------------------------------------------
    
    data = []

    rows = target_table.find_all("tr")

    for row in rows[1:]:

        cells = row.find_all("td")

        if not cells:
            continue

        row_data = []
        pdf_url = ""

        for cell in cells:

            text = cell.get_text(
                " ",
                strip=True
            )

            row_data.append(text)

            # Check links inside this cell
            for link in cell.find_all("a", href=True):

                href = link.get("href")

                if href and ".pdf" in href.lower():

                    pdf_url = href

                    break


        # Add PDF URL as an additional column
        row_data.append(pdf_url)

        data.append(row_data)


    # Add our additional column
    headers.append("PDF_URL")


    df = pd.DataFrame(
        data,
        columns=headers
    )

    df.to_csv(
        "sci_judgments.csv",
        index=False,
        encoding="utf-8-sig"
    )
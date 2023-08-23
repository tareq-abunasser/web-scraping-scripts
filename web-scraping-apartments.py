import os
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_place_from_details(soup):
    place_div = soup.find('div', class_='_1075545d e3cecb8b _5f872d11')
    if place_div:
        place_span = place_div.find('span', {'aria-label': 'Location'})
        if place_span:
            return place_span.text
        else:
            return "Place <span> not found inside the specified <div>"
    else:
        return "Details <div> not found on the page."


def get_details_from_div(details_div):
    data = {}
    try:
        if details_div:
            data['area'] = details_div.find('span', text='Area (m²)').find_next_sibling('span').text
            data['price'] = details_div.find('span', text='Price').find_next_sibling('span').text
            data['type'] = details_div.find('span', text='Type').find_next_sibling('span').text
            data['bathrooms'] = details_div.find('span', text='Bathrooms').find_next_sibling('span').text
            data['bedrooms'] = details_div.find('span', text='Bedrooms').find_next_sibling('span').text
            data['level'] = details_div.find('span', text='Level').find_next_sibling('span').text
            return data
        else:
            return "Details <div> not found on the page."
    except:
        data['level'] = ""
        return data


def download_image(soup, img_filename):
    img_element = soup.find('img', {'role': 'presentation', 'class': '_5b8e3f79'})
    if img_element:
        img_url = img_element['src']
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            with open(img_filename, 'wb') as img_file:
                img_file.write(img_response.content)
            return f"Image downloaded as {img_filename}"
        else:
            return f"Failed to download image. Status code: {img_response.status_code}"
    else:
        return "Image <img> not found on the page."


def scrape_page(url):
    data_list = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        listing_lis = soup.find_all('li', class_='undefined', attrs={'aria-label': 'Listing'})

        if listing_lis:
            for listing_li in listing_lis:
                link_element = listing_li.find('a')
                if link_element:
                    link = link_element.get('href')
                    details_url = f"https://www.dubizzle.com.eg{link}"
                    print(f"Link: {details_url}")

                    details_response = requests.get(details_url)
                    if details_response.status_code == 200:
                        details_soup = BeautifulSoup(details_response.content, 'html.parser')
                        place = get_place_from_details(details_soup)
                        # print(f"Place: {place}")

                        details_div = details_soup.find('div', class_='_241b3b1e')
                        details_data = get_details_from_div(details_div)
                        # for key, value in details_data.items():
                        #     print(f"{key.capitalize()}: {value}")

                        img_filename = f"{place}-{os.path.basename(details_data['price']) + '.jpg'}"
                        download_result = download_image(details_soup, img_filename)
                        # print(download_result)

                        print("#" * 10)
                        data_list.append({
                            'Place': place,
                            'Area': details_data['area'],
                            'Price': details_data['price'],
                            'Type': details_data['type'],
                            'Bathrooms': details_data['bathrooms'],
                            'Bedrooms': details_data['bedrooms'],
                            'Level': details_data['level'],
                            'Image Filename': img_filename
                        })

                    else:
                        print(f"Failed to retrieve details page. Status code: {details_response.status_code}")
                else:
                    print("Link <a> not found inside the specified <li>")
            data_frame = pd.DataFrame(data_list)

            excel_filename = 'property_data.xlsx'
            data_frame.to_excel(excel_filename, index=False)
            print(f"Data saved to {excel_filename}")
        else:
            print("Listing <li> not found on the page.")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


# URL of the webpage to scrape
page_nums = 5
base_url = "https://www.dubizzle.com.eg/en/properties/apartments-duplex-for-sale/"
for page_num in range(1, page_nums + 1):
    print("*" * 100)
    print(f"Page {page_num}")
    if page_num == 1:
        url = f'{base_url}?filter=type_eq_1'
    else:
        url = f'{base_url}/?page={page_num}&filter=type_eq_1'

    scrape_page(url)

from selenium import webdriver 
from bs4 import BeautifulSoup


urls = [
    '@freecodecamp'
]


def browse():
    driver = webdriver.Chrome()
    for url in urls:
        driver.get('https://www.youtube.com/{}/videos'.format(urls))
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'lxml')
        titles = soup.find_all('a', id='video-title-link')
        views = soup.find_all('span', class_='inline-metadata-item style-scope ytd-video-meta-block')
        video_urls = soup.find_all('a', id='video-title-link')

        i = 0 # iteration on views
        j = 0 # iteration on urls

        print("Channels: {}".format(urls))

        for title in titles[:10]:
            print('\n{}\t{}\t{}\thttps://www.youtube.com{}'.format(title.text, views[i].text, views[i+1].text, video_urls[i].get('href')))
            i +=2
            j +=1

    


    


browse()
import json 
import re
import os


base_directory = os.path.dirname(os.path.abspath(__file__)) 

file_path = os.path.join(base_directory, '..', '..', 'data', 'result.json')  
menu_list_path = os.path.join(base_directory, 'menu_list.json') 
new_menu_list_path = os.path.join(base_directory, 'new_menu_list.json') 



restaurant_keys = [
    "문창회관 식당",
    "학생회관 학생 식당",
    "자유",
    "진리",
    "웅비",
    "금정회관 교직원 식당",
    "금정회관 학생 식당"
]

def clean_menu(menu): 
    
    menu = re.sub(r'(\d+kcal|\d+g|영업시간\(\d{0,2}:\d{0,2}~\d{0,2}:\d{0,2}\)|운영시간\(:~:\)|없음|문의:\s*\d+-\d+-\d+)', '', menu)
    menu = re.sub(r'\d+', '', menu)  #수
    menu = re.sub(r'운영시간\(:~:\)', '', menu)
    menu = re.sub(r'제외', '', menu)
    
    menu = re.sub(r'\(+C+\)', '', menu)
    menu = re.sub(r'\(+C', '', menu)
    menu = re.sub(r'C+\)', '', menu)
    menu = re.sub(r'C', '', menu)


    menu = re.sub(r'\(+D+\)', '', menu)
    menu = re.sub(r'\(+D', '', menu)
    menu = re.sub(r'D+\)', '', menu)
    menu = re.sub(r'D', '', menu)
    
    
    menu = re.sub(r'\(+P+\)', '', menu)
    menu = re.sub(r'\(+P', '', menu)
    menu = re.sub(r'P+\)', '', menu)
    menu = re.sub(r'P', '', menu)

    
    menu = re.sub(r'\(+E+\)', '', menu)
    menu = re.sub(r'\(+E', '', menu)
    menu = re.sub(r'E+\)', '', menu)
    menu = re.sub(r'E', '', menu)

    
    menu = re.sub(r'\(+F+\)', '', menu)
    menu = re.sub(r'\(+F', '', menu)
    menu = re.sub(r'F+\)', '', menu)
    menu = re.sub(r'F', '', menu)

    
    menu = re.sub(r'\(+D+\)', '', menu)
    menu = re.sub(r'\(+D', '', menu)
    menu = re.sub(r'D+\)', '', menu)
    menu = re.sub(r'D', '', menu)

    
    menu = re.sub(r'\(+B+\)', '', menu)
    menu = re.sub(r'\(+B', '', menu)
    menu = re.sub(r'B+\)', '', menu)
    menu = re.sub(r'B', '', menu)

    menu = re.sub(r'&lt;밥 없는 날&gt;', '', menu)



    menu = re.sub(r'\s+', ' ', menu) #공백
    
    return menu.strip()



def extract_menu_items_from_file(file_path):
    restaurant_menus = {restaurant: set() for restaurant in restaurant_keys}

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for restaurant_data in data:
        for entry in restaurant_data:
            if entry['res'] in restaurant_keys:
                for meal in entry['meals']:
                    try:
                        menu = meal['menu'].replace('\n<br>', ', ')
                        cleaned_menu = clean_menu(menu)

                        if entry['res'] in ["자유", "웅비"]:
                            menu_items = [item.strip() for item in re.split(r'[ ,/.]', cleaned_menu) if item.strip()]
                        else:
                            menu_items = [item.strip() for item in re.split(r'[,/]', cleaned_menu) if item.strip()]

                        #괄호
                        processed_menu_items = []
                        for item in menu_items:
                            
                            if item.startswith("(") and item.endswith(")"):
                                processed_menu_items.append(item)
                            
                            elif item.startswith("("):  
                                processed_menu_items.append(item[1:]) 
                            elif item.endswith(")"):  
                                processed_menu_items.append(item[:-1]) 
                            else:
                                processed_menu_items.append(item) 

                        
                        restaurant_menus[entry['res']].update(processed_menu_items)

                    except KeyError:
                        pass

    return restaurant_menus

def extract_all_menu_items():    #요거는 메뉴 추출을 단독으로 하는 함수 (중복확인 없이 그냥)  //딕셔너리

    all_restaurant_menus = extract_menu_items_from_file(file_path)
    
    return {restaurant: list(items) for restaurant, items in all_restaurant_menus.items()}


def convertTojson(data, wishToMakePath):

    data = {restaurant: list(menu_items) for restaurant, menu_items in data.items()}
    
    with open(wishToMakePath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_existing_menus(menu_list_path):   #딕셔너리
    if os.path.exists(menu_list_path):
        with open(menu_list_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {restaurant: [] for restaurant in restaurant_keys}
    

def update_menus():
    existing_menus = load_existing_menus(menu_list_path) 
    existing_menu_sets = {restaurant: set(existing_menus[restaurant]) for restaurant in restaurant_keys}  # 메뉴-> set

    new_menus = extract_menu_items_from_file(file_path)  
    new_menu_entries = {restaurant: set() for restaurant in restaurant_keys}  # 새로운 메뉴 항목만 추출 (빈 set으로 시작)

    new_items_found = False 

    # 새로운 항목 -> 기존 메뉴 업데이트 및 new_menu_list.json에 추가

    for restaurant, menu_items in new_menus.items():
        new_items = menu_items - existing_menu_sets[restaurant] 

        if new_items: 
            print(f"새로운 메뉴 항목이 {restaurant}에 추가됨: {new_items}") #디버깅

            new_menu_entries[restaurant].update(new_items)  # 새로운 메뉴만!!!!!! 추가
            existing_menu_sets[restaurant].update(new_items) 
            new_items_found = True  


    if new_items_found:
        new_menu_entries_as_list = {restaurant: list(menu_items) for restaurant, menu_items in new_menu_entries.items() if menu_items}
        convertTojson(new_menu_entries_as_list, new_menu_list_path) 

    else:
        print('새로운 메뉴가 없습니다.') #디버깅

 
    updated_menus = {restaurant: list(existing_menu_sets[restaurant]) for restaurant in restaurant_keys}
    convertTojson(updated_menus, menu_list_path)  # menu_list.json에는 기존 & 새로운 메뉴 모두 누적


#main

if not os.path.exists(menu_list_path):
    result = extract_all_menu_items()  #result = 딕셔너리!!!! ex) 문창 : [밥, 국 ...]
    convertTojson(result, menu_list_path)  #먼저 호출해서 menu_list를 일단 생성해


update_menus()  #추가된 놈들을 업데이트해서 기존 menu_list.json에 추가, new_menu_list.json 만들어서 새 메뉴 업뎃

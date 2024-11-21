from django.shortcuts import render

REGION_DATA = {
    '경상북도 청송군': {'info': '사과와 주왕산으로 유명한 경상북도의 지역입니다.'},
    '전라남도 곡성군': {'info': '섬진강과 기차마을이 있는 전라남도의 지역입니다.'},
}

def data_list(request):
    context = {'regions': REGION_DATA.keys()}  # 지역 이름 리스트 전달
    return render(request, 'datas/data_list.html', context)

def region_detail(request, region_name):
    context = {
        'region_name': region_name,
        'region_info': REGION_DATA[region_name]['info'],
    }
    return render(request, 'datas/region_detail.html', context)

def tour_detail(request, region_name):
    context = {'region_name': region_name}
    return render(request, 'datas/tour_detail.html', context)

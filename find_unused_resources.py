# -*- coding: utf-8 -*-
import os
import re
import codecs
import pprint

PROJECT_DIRECTORY = ''
EXCLUDE_DIRECTORY = ['.git']
EXCLUDE_FILE_PATTERNS = [r'\.ipa$', r'\.pbxproj$']

TARGET_FILE_EXTENSIONS = ['.plist',
                          '.h',
                          '.m',
                          '.cpp',
                          '.mm',
                          '.swift',
                          '.storyboard',
                          '.xib',
                          '.html',
                          '.css']
IMAGE_EXTENSION_RE_PATTERNS = [r'\.png$', r'\.pdf$']
LOCALIZABLE_STRING_PATH = ''


def is_exclude_pattern(file_name, exclude_patterns):
    for exclude_file_pattern in exclude_patterns:
        exclude = re.search(exclude_file_pattern, file_name)
        if exclude:
            return True
    return False


def unused_img_files(images):
    images_copy = list(images)
    directories = []
    for directory in EXCLUDE_DIRECTORY:
        directories.append(os.path.join(PROJECT_DIRECTORY, directory))

    for root, dirs, files in os.walk(PROJECT_DIRECTORY, topdown=True):
        # exclude path
        if root in directories:
            dirs[:] = []
            continue
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # exclude file pattern
            if is_exclude_pattern(file_name, EXCLUDE_FILE_PATTERNS):
                continue
            ext = os.path.splitext(file_name)[1]
            if ext not in TARGET_FILE_EXTENSIONS:
                continue
            with open(file_path) as f:
                for line in f:
                    removed_image = None
                    for image in images_copy:
                        if image in line:
                            removed_image = image
                    if removed_image is not None:
                        images_copy.remove(removed_image)
    return images_copy


def unused_localized_string_in_files(localizable_strings):
    localizable_strings_copy = set(localizable_strings)
    directories = []
    for directory in EXCLUDE_DIRECTORY:
        directories.append(os.path.join(PROJECT_DIRECTORY, directory))
    for root, dirs, files in os.walk(PROJECT_DIRECTORY, topdown=True):
        # exclude path
        if root in directories:
            dirs[:] = []
            continue
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # exclude file pattern
            if is_exclude_pattern(file_name, EXCLUDE_FILE_PATTERNS):
                continue
            ext = os.path.splitext(file_name)[1]
            if ext not in TARGET_FILE_EXTENSIONS:
                continue
            with open(file_path) as f:
                for line in f:
                    removed_string = None
                    for localizable_string in localizable_strings_copy:
                        if localizable_string in line:
                            removed_string = localizable_string
                    if removed_string is not None:
                        localizable_strings_copy.remove(removed_string)
    return localizable_strings_copy


def main():
    pp = pprint.PrettyPrinter(indent=4)
    directories = []
    for directory in EXCLUDE_DIRECTORY:
        directories.append(os.path.join(PROJECT_DIRECTORY, directory))

    print '============================================================='
    print 'Start Searching Unused Resources'
    print 'Project Directory: ' + os.path.abspath(PROJECT_DIRECTORY)
    print '============================================================='
    images = set()
    image_paths = {}
    for root, dirs, files in os.walk(PROJECT_DIRECTORY, topdown=True):
        # exclude path
        if root in directories:
            dirs[:] = []
            continue
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # exclude file pattern
            if is_exclude_pattern(file_name, EXCLUDE_FILE_PATTERNS):
                continue

            is_image = False
            for re_pattern in IMAGE_EXTENSION_RE_PATTERNS:
                if re.search(re_pattern, file_name):
                    is_image = True
                    # extension을 지웁니다. (ex: btn_common_x.png -> btn_common_x 로 검색하기 위해)
                    file_name = re.sub(re_pattern, '', file_name)
                    break
            if not is_image:
                continue
            # @1x, @2x, @3x 지우기
            file_name = re.sub(r'@\dx', '', file_name)
            # _1, _2, _3 지우기
            # 제작하던 프로젝트에서 image_1.png, image_2.png ... 이용하여 애니메이션을 넣는 부분이 있어서 이 부분을 한 번에 처리하기 위함입니다
            file_name = re.sub(r'_\d+$', '', file_name)

            images.add(file_name)
            if image_paths.get(file_name) is None:
                image_paths[file_name] = file_path
    unused_images = unused_img_files(list(images))
    unused_image_paths = {}
    for unused_image in unused_images:
        unused_image_paths[unused_image] = image_paths.get(unused_image)
    pp.pprint(unused_image_paths)
    print '============================================================='
    print 'Complete Searching Unused Images .'
    print '============================================================='

    localizable_strings = set()
    localizable_path = os.path.join(PROJECT_DIRECTORY, LOCALIZABLE_STRING_PATH)
    with codecs.open(localizable_path, encoding='utf-16') as f:
        for line in f:
            line = line.rstrip('\n\0')
            finds = re.findall(r'\"(.+?)\" \= \"(.+?)\"', line)
            if len(finds) > 0:
                localizable_strings.add(finds[0][0].encode('utf-8'))
    unused_strings = unused_localized_string_in_files(localizable_strings)
    pp.pprint(unused_strings)
    print '============================================================='
    print 'Complete Searching Unused Localizable Strings .'
    print '============================================================='


if __name__ == '__main__':
    main()

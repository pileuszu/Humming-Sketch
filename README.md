# Humming to MIDI Converter

허밍을 MIDI로 변환하는 파이썬 프로젝트입니다.

## 기능
- 허밍 음성(.wav) 파일을 MIDI로 변환
- 피치 검출 및 음표 길이 추정
- MIDI 노트 생성 및 저장
- 노이즈 제거 및 음정 보정

## 설치 방법

```bash
pip install -r requirements.txt
```

## 사용 방법

1. source 폴더에 변환하고자 하는 .wav 파일을 넣습니다.
2. 다음 명령어를 실행합니다:

```bash
python humming_to_midi.py --input source/your_humming.wav --output output/result.mid
```

## 프로젝트 구조
```
.
├── README.md
├── requirements.txt
├── humming_to_midi.py     # 메인 스크립트
├── src/
│   ├── pitch_detection.py # 피치 검출 모듈
│   ├── note_detection.py  # 음표 검출 모듈
│   └── midi_converter.py  # MIDI 변환 모듈
├── source/                # 입력 WAV 파일 디렉토리
└── output/               # 출력 MIDI 파일 디렉토리
``` 
import argparse
import soundfile as sf
from src.pitch_detection import PitchDetector
from src.note_detection import NoteDetector
from src.midi_converter import MIDIConverter

def main():
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description='허밍을 MIDI로 변환')
    parser.add_argument('--input', type=str, required=True, help='입력 WAV 파일 경로')
    parser.add_argument('--output', type=str, required=True, help='출력 MIDI 파일 경로')
    parser.add_argument('--tempo', type=float, default=120.0, help='템포 (BPM)')
    parser.add_argument('--min-note', type=float, default=0.1, help='최소 음표 길이 (초)')
    parser.add_argument('--grid', type=float, default=0.25, help='양자화 그리드 크기 (1.0 = 4분음표)')
    args = parser.parse_args()
    
    try:
        # 오디오 파일 로드
        print(f"오디오 파일 로드 중: {args.input}")
        audio_data, sr = sf.read(args.input)
        
        # 모노로 변환 (스테레오인 경우)
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # 피치 검출
        print("피치 검출 중...")
        pitch_detector = PitchDetector(sr=sr)
        midi_notes, confidence = pitch_detector.get_midi_notes(audio_data)
        
        # 음표 검출
        print("음표 검출 중...")
        note_detector = NoteDetector(sr=sr, min_note_length=args.min_note)
        notes = note_detector.detect_notes(midi_notes, confidence)
        
        # 음표 양자화
        print("음표 양자화 중...")
        quantized_notes = note_detector.quantize_notes(notes, tempo=args.tempo, grid=args.grid)
        
        # MIDI 파일 생성
        print(f"MIDI 파일 생성 중: {args.output}")
        midi_converter = MIDIConverter(tempo=args.tempo)
        midi_converter.notes_to_midi(quantized_notes, args.output)
        
        print("변환 완료!")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main()) 
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processing import Landmark,PoseFrame,CycleProtocol,CycleCounter,angle,process


PROTOCOL=CycleProtocol('synthetic-test-only',40,140,.1,.4,4,.25,.8,.1,.5,'low_high_low')

def frame(timestamp, value=30, visible=True):
    points=[None]*33
    points[11]=Landmark(1,0,0,1)
    points[13]=Landmark(0,0,0,1)
    points[15]=Landmark(math.cos(math.radians(value)),math.sin(math.radians(value)),0,1 if visible else 0)
    return PoseFrame(timestamp,points)


class ProcessingTests(unittest.TestCase):
    def test_requires_explicit_reviewable_protocol_and_coordinates(self):
        with self.assertRaises(ValueError):replace(PROTOCOL,high=20)
        with self.assertRaises(ValueError):angle(frame(0),(11,13,15),min_visibility=.8,coordinate_space='image')
        with self.assertRaises(ValueError):angle(frame(0),(11,11,15),min_visibility=.8,coordinate_space='world')

    def test_world_angle_preserves_missing_values(self):
        self.assertAlmostEqual(angle(frame(0,90),(11,13,15),min_visibility=.8,coordinate_space='world'),90)
        self.assertIsNone(angle(frame(0,90,False),(11,13,15),min_visibility=.8,coordinate_space='world'))
        points=list(frame(0).landmarks);points[15]=Landmark(float('nan'),0,0,1)
        self.assertIsNone(angle(PoseFrame(0,points),(11,13,15),min_visibility=.8,coordinate_space='world'))

    def test_image_angle_corrects_non_square_aspect_ratio(self):
        points=[None]*33
        points[11],points[13],points[15]=Landmark(.5,.5,0,1),Landmark(0,0,0,1),Landmark(1,0,0,1)
        result=angle(PoseFrame(0,points),(11,13,15),min_visibility=.8,coordinate_space='image',image_size=(200,100))
        self.assertAlmostEqual(result,math.degrees(math.atan(.5)))

    def test_only_full_stable_cycles_count(self):
        counter=CycleCounter(PROTOCOL)
        for i,value in enumerate([30,30,80,150,150,90,30,30]):counter.step(i*.1,value)
        self.assertEqual(counter.count,1)
        counter.step(.8,150) # No stable high endpoint or return yet.
        self.assertEqual(counter.count,1)

    def test_reverse_direction_and_partial_start(self):
        counter=CycleCounter(replace(PROTOCOL,direction='high_low_high'))
        for i,value in enumerate([30,30,150,150,30,30,150,150]):counter.step(i*.1,value)
        self.assertEqual(counter.count,1)

    def test_missing_frame_or_time_gap_never_completes_a_bridged_cycle(self):
        for missing in [None,float('nan')]:
            counter=CycleCounter(PROTOCOL)
            for i,value in enumerate([30,30,150,150,missing,30,30]):counter.step(i*.1,value)
            self.assertEqual(counter.count,0)
        counter=CycleCounter(PROTOCOL)
        for stamp,value in [(0,30),(.1,30),(.2,150),(.3,150),(1,30),(1.1,30)]:counter.step(stamp,value)
        self.assertEqual(counter.count,0)

    def test_rejected_result_has_no_repetition_or_quality_value(self):
        rows=[frame(i*.1,visible=False) for i in range(10)]
        result=process(rows,(11,13,15),PROTOCOL,coordinate_space='world')
        self.assertEqual(result.status,'rejected');self.assertIsNone(result.repetition_count);self.assertIsNone(result.quality_score)
        self.assertIn('INSUFFICIENT_VISIBILITY',result.reason_codes);self.assertIsNone(result.model_version)

    def test_corrupt_timing_is_error_but_recording_gap_is_rejection(self):
        result=process([frame(0),frame(0)],(11,13,15),PROTOCOL,coordinate_space='world')
        self.assertEqual(result.status,'error')
        result=process([frame(0),frame(1)],(11,13,15),PROTOCOL,coordinate_space='world')
        self.assertEqual(result.status,'rejected');self.assertIn('INTERRUPTED_TRACKING',result.reason_codes)

    def test_still_visible_sequence_can_have_a_real_zero(self):
        result=process([frame(i*.1) for i in range(10)],(11,13,15),PROTOCOL,coordinate_space='world')
        self.assertEqual(result.status,'success');self.assertEqual(result.repetition_count,0)
        self.assertIsNone(result.quality_score)


if __name__=='__main__':unittest.main()

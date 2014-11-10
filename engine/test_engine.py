import engine
import unittest
import os
from timer import Timer

class TestEngine(unittest.TestCase):
        
    def setUp(self):
        self.max_time = 0.5
        self.ti = Timer()

    def test_plan_empty(self):
        scheduleditems = engine.plan({}, ['some_stuff_doesnt_matter'])
        self.assertItemsEqual([], scheduleditems)

    def test_plan(self):
        preferences1 = { "today" : [ [1, 3], [5,  8]], "thisweek": [ [20,21],[32, 50], [50, 45]] }
        tasks1 = { "123" : { "when": 0, "due": 4, "duration": 5},
                "345" : { "when": 1, "comes_after": "123", "due": 50, "duration": 10}} 
         
        self.assertEqual(engine.plan(tasks1, preferences1), {'123': [[1, 3]], '345': [[20, 21], [32, 41]]})
        preferences2 = { "today" : [ [8, 16], [17,  20]], "thisweek": [ [1, 8], [8, 34], [37, 100]] }
        tasks2 = { "1" : { "when": 0, "due": 18, "duration": 9}}
        self.assertNotEqual(engine.plan(tasks2, preferences2), {'1': [[8, 17]]})
        self.assertEqual(engine.plan(tasks2, preferences2), {'1': [[8, 16], [17,18]]})
        preferences3 = { "today" : [ [8, 10], [17,  20]], "thisweek": [ [1, 8], [8, 34], [37, 100]] }
        tasks3 = { "1" : { "when": 0, "due": 18, "duration": 4}}
        self.assertEqual(engine.plan(tasks3, preferences3), {'1': [[8, 10], [17,18]]})

    def test_plan_distribute_rouhly_equally(self):
        preferences = { "today" : [ [0, 8]]}
        tasks = { "123" : { "when": 0}}
        self.assertEqual(engine.plan(tasks, preferences), {'123': [[0, 8]]})
        tasks = { "123" : { "when": 0}, "345" : { "when": 0}}
        self.assertNotEqual(engine.plan(tasks, preferences), {'345': [[2, 8]], '123': [[0, 1]]})
        preferences= { "today" : [ [0, 2]]}
        self.assertEqual(engine.plan(tasks, preferences), {'345': [[0, 1]], '123': [[1, 2]]})
        preferences = { "today" : [ [0, 4]]}
        self.assertEqual(engine.plan(tasks, preferences), {'345': [[0, 2]], '123': [[2, 4]]})
        preferences = { "today" : [ [0, 9]]}
        tasks = { "123" : { "when": 0}, "345" : { "when": 0}, "567" : { "when" : 0} }
        self.assertEqual(engine.plan(tasks, preferences), {'345': [[0, 3]], '123': [[3, 6]], "567": [[6,9]]})
        preferences = { "today" : [ [0, 8]]}
        self.assertEqual(engine.plan(tasks, preferences), {'345': [[0, 3]], '123': [[3, 6]], "567": [[6,8]]})

    def test_plan_follow_duration(self):
        preferences1 = { "today" : [ [0, 8]]}
        tasks1 = { "123" : { "when": 0, "duration": 5}, "345" : { "when": 0}}
        self.assertEqual(engine.plan(tasks1, preferences1),{'345': [[5, 8]], '123': [[0, 5]]}) 
        tasks1 = { "123" : { "when": 0, "duration": 4}, "345" : { "when": 0}}
        self.assertEqual(engine.plan(tasks1, preferences1),{'345': [[4, 8]], '123': [[0, 4]]}) 
        preferences = { "today" : [ [0, 9]]}
        tasks = { "123" : { "when": 0, "duration": 5}, "345" : { "when": 0}, "567" : { "when" : 0} }
        self.assertEqual(engine.plan(tasks, preferences), {'345': [[5, 7]], '123': [[0, 5]], "567": [[7,9]]})

    def test_plan_follow_duration(self):
        preferences = { "today" : [ [0, 9]]}
        tasks = { "123" : { "when": 0, "duration": 5}, "345" : { "when": 0}, "567" : { "when" : 0, "duration": 1} }
        
        self.assertEqual(engine.plan(tasks, preferences), {'345': [[0, 3]], '123': [[3, 8]], '567': [[8, 9]]})

    def test_plan_20140513A(self):
        preferences = { "today" : [ [0, 4], [6,8]]}
        tasks = { "123" : { "when": 0, "duration": 5}}
        self.assertEqual(engine.plan(tasks, preferences), {'123': [[0, 4], [6,7]]})

    def test_plan_20140513B(self):
        preferences = { "today" : [ [0, 4], [6,8]], "thisweek": [[8,12]]}
        tasks = { "123" : { "when": 0, "duration": 6}, "345" : { "when": 1, "duration": 2}}
        self.assertEqual(engine.plan(tasks, preferences), {'123': [[0, 4], [6,8]], '345': [[8,10]]})
        preferences = { "today" : [ [0, 4], [6,9]], "thisweek": [[9,12]]}
        self.assertEqual(engine.plan(tasks, preferences), {'123': [[0, 4], [6,8]], '345': [[9,11]]})
        preferences = { "today" : [ [0, 4], [6,7]], "thisweek": [[7,12]]}
        self.assertEqual(engine.plan(tasks, preferences), {'123': [[0, 4], [6,7]], '345': [[7,9]]})

    def test_timing_A(self):
        preferences = { "today" : [ [0, 4], [6,8]], "thisweek": [[6,12]]}
        tasks = { "123" : { "when": 0, "duration": 6}, "345" : { "when": 1, "duration": 2}}
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

        tasks = { "123" : { "when": 0}, "345" : { "when": 0}, "567" : { "when" : 0} }
        preferences = { "today" : [ [0, 8]]}
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)


        preferences = { "today" : [ [0, 9]]}
        tasks = { "123" : { "when": 0}, "345" : { "when": 0}, "567" : { "when" : 0} }
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

        preferences = { "today" : [ [0, 4], [6,8]]}
        tasks = { "123" : { "when": 0, "duration": 5}}
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_plan_20140519A(self):
        # do not spread tasks too much when lengths of intervals become too
        # small
        preferences = { "today" : [ [0, 3], [4,5], [6,7]]}
        tasks = { "123" : { "when": 0, "duration": 4}}
        self.assertEqual(engine.plan(tasks, preferences), {'123': [[0, 3], [4, 5]]})

    def test_plan_20140618A(self):
        tasks = {67L: {'when': 0}, 68L: {'when': 0}, 69L: {'when': 1}}
        preferences = {'thisweek': [[73, 109]], 'today': [[0, 12]]}
        desired_plan = {67L: [[0, 6]], 68L: [[6, 12]], 69L: [[73, 109]]}
        self.assertEqual(engine.plan(tasks, preferences), desired_plan)

    def test_timing_20140619A(self):
        tasks = {67L: {'when': 0}, 68L: {'when': 0}, 69L: {'when': 1}}
        preferences = {'thisweek': [[73, 109]], 'today': [[0, 12]]}
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_overlaps_weight_20140619B(self):
        # this shows that setting overlaps weight<1 makes the scheduling succeed
        # fast for the following schedule which used to be problematic
        tasks = {2L: {'when': 0}, 3L: {'when': 0}, 4L: {'when': 0}}
        preferences = {'today': [[0, 16]]}
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140623A(self):
        tasks = {32L: {'duration': 9, 'when': 0}, 31L: {'when': 0}}
        preferences =  {'thisweek': [[384, 432]], 'today': [[0, 32]]}
        schedule = {32L: [[0, 9]], 31L: [[9, 32]]}
        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140623B(self):
        tasks =  {32L: {'duration': 9, 'when': 0}, 31L: {'when': 1}}
        preferences =  {'thisweek': [[383, 431], [99, 151]], 'today': [[0, 31]]}
        schedule =   {32L: [[0, 9]], 31L: [[383, 431], [99, 151]]}
        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140623C(self):
        tasks =  {33L: {'when': 1}, 31L: {'when': 1}}
        preferences =  {'thisweek': [[94, 142], [386, 438]], 'today': [[0, 30]]}
        schedule = {33L: [[0, 30], [94, 129]], 31L: [[129, 142], [386, 438]]}
        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140623D(self):
        tasks =  {37L: {'comes_after': 38L, 'when': 0}, 38L: {'when': 0}, 39L: {'comes_after': 37L, 'when': 0}}
        preferences =  {'thisweek': [[78, 126], [370, 422]], 'today': [[0, 14]]}
        schedule =   {37L: [[5, 10]], 38L: [[0, 5]], 39L: [[10, 14]]}
        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140623E(self):
        tasks =  {37L: {'when': 0}, 38L: {'when': 0}, 39L: {'when': 0, 'due': 4}}
        preferences =  {'thisweek': [[60, 108], [352, 404]], 'today': [[0, 20]]}
        schedule =   {37L: [[4, 12]], 38L: [[12, 20]], 39L: [[0, 4]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140624A(self):
        tasks =  {45L: {'when': 0}, 47L: {'when': 0, 'due': 8}}
        preferences =  {'thisweek': [[288, 340], [100, 132], [188, 220]], 'today': [[0, 44]]}
        schedule =   {45L: [[8, 44]], 47L: [[0, 8]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140624B(self):
        tasks =  {45L: {'when': 0}, 46L: {'duration': 4, 'comes_after': 45L, 'when': 0, 'due': 9}}
        preferences =  {'thisweek': [[289, 341], [101, 133], [189, 221]], 'today': [[0, 45]]}
        schedule =   {45L: [[0, 5]], 46L: [[5, 9]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140624C(self):
        tasks =  {45L: {'when': 0, 'due': 28}, 47L: {'when': 0, 'due': 4}}
        preferences =  {'thisweek': [[284, 336], [96, 128], [184, 216]], 'today': [[0, 40]]}
        schedule =   {45L: [[4, 28]], 47L: [[0, 4]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140624D(self):
        tasks =  {48L: {'when': 0}, 45L: {'comes_after': 48L, 'when': 0, 'due': 31}}
        preferences =  {'thisweek': [[283, 335], [95, 127], [183, 215]], 'today': [[0, 39]]}
        schedule =   {48L: [[0, 15]], 45L: [[15, 31]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140624E(self):
        tasks =  {48L: {'when': 0}, 49L: {'when': 0}, 45L: {'comes_after': 48L, 'when': 0, 'due': 26}}
        preferences =  {'thisweek': [[278, 330], [90, 122], [178, 210]], 'today': [[0, 34]]}
        schedule =   {48L: [[0, 12]], 49L: [[23, 34]], 45L: [[12, 23]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140625A(self):
        tasks =  {50L: {'duration': 36, 'when': 0}, 51L: {'duration': 8, 'when': 0}}
        preferences =  {'thisweek': [[188, 240], [88, 120]], 'today': [[0, 32]]}
        schedule =   {50L: [[0, 24]], 51L: [[24, 32]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140625B(self):
        tasks =  {50L: {'when': 0, 'due': 3}, 52L: {'comes_after': 50L, 'when': 0, 'due': 1}}
        preferences =  {'thisweek': [[186, 238], [86, 118]], 'today': [[0, 30]]}
        schedule =   {50L: [[0, 1]], 52L: [[1, 2]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140625C(self):
        tasks =  {50L: {'when': 1}, 52L: {'comes_after': 50L, 'when': 1, 'due': 63}}
        preferences =  {'thisweek': [[52, 84], [152, 204]], 'today': []}
        schedule =   {50L: [[52, 57]], 52L: [[57, 63]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_constrain_preferences_with_meetings(self):
        preferences =  {'thisweek': [[52, 84], [152, 204]], 'today': []}
        meetings =  [[52, 64], [83,91], [100, 130]]
        self.assertItemsEqual(engine.constrain_preferences_with_meetings(preferences, meetings)["thisweek"], [[64, 83],[152, 204]]) 

    def test_schedule_20140626(self):
        tasks =  {1L: {'when': 0}}
        meetings =  [[17, 21]]
        preferences =  {'thisweek': [[93, 145]], 'today': [[0, 17], [21, 25]]}
        schedule =   {1L: [[0, 17], [21, 25]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140815(self):
        tasks =  {416L: {'when': 0}, 414L: {'flex': 36, 'when': 1}}
        preferences =  {'thisweek': [[251, 299], [333, 397], [443, 453], [469, 491], [539, 551], [565, 583], [633, 669]], 'today': []}
        schedule =  {414L: [[251, 299], [333, 397], [443, 453], [469, 491], [539, 551], [565, 583], [633, 669]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140816A(self):
        tasks =  {417L: {'when': 1}, 414L: {'comes_after': 417L, 'when': 1, 'due': 169}}
        preferences =  {'thisweek': [[164, 172]], 'today': []}
        schedule =  {417L: [[164, 166]], 414L: [[166, 169]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)


    def test_schedule_20140816B(self):
        tasks =  {417L: {'when': 1}, 414L: {'duration': 2, 'comes_after': 417L, 'when': 1, 'due': 169}}
        preferences =  {'thisweek': [[164, 172]], 'today': []}
        schedule =  {417L: [[164, 167]], 414L: [[167, 169]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    @unittest.skip("engine algorithm not able to deal with this test")
    def test_schedule_20140816C(self):
        # The reason is that the duration of task 417L is only 1, and
        # done_trying concludes from that "yes", I cannot reduce this anymore.
        # Trying to solve this would require probably backtracking, so a
        # violation causes to crash the system if other tasks are present (no
        # schedule exists just).
        tasks =  {417L: {'when': 1}, 414L: {'duration': 1, 'comes_after': 417L, 'when': 1, 'due': 169}}
        preferences =  {'thisweek': [[164, 172]], 'today': []}
        schedule =  {417L: [[164, 171]], 414L: [[171, 172]]}

        # That is the wrong schedule, task 417L now all of a sudden goes to 171
        # and task 414L has both its duration violated and the due date for no
        # good reason.
        self.assertNotEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)
        # we should get this:
        schedule =  {417L: [[164, 168]], 414L: [[168, 169]]}
        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_20140816D(self):
        # duration not satisfied
        tasks =  {417L: {'when': 1}, 414L: {'comes_after': 417L, 'when': 1, 'due': 160}}
        preferences =  {'thisweek': [[159, 167]], 'today': []}
        schedule =  {417L: [[159, 160]], 414L: [[160, 161]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_schedule_no_tasks_today(self):
        tasks =  {528L: {'when': 1}, 529L: {'when': 1}}
        preferences =  {'thisweek': [[83, 123], [165, 201], [261, 297], [357, 393]], 'today': [[0, 15]]}
        schedule =  {528L: [[0, 15], [83, 123], [165, 192]], 529L: [[192, 201], [261, 297], [357, 393]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)

    def test_due_date_in_combination_with_comes_after(self):
        tasks =  {533L: {'when': 1, 'due': 5}, 534L: {'comes_after': 535L, 'when': 1, 'due': 409}, 535L: {'when': 1}}
        preferences =  {'thisweek': [[0, 32], [93, 128], [189, 224], [285, 320], [381, 416]]}
        schedule = {533L: [[2, 5]], 534L: [[5, 32], [93, 128], [189, 224], [285, 320], [381, 409]], 535L: [[0, 2]]}

        self.assertEqual(engine.plan(tasks, preferences), schedule)
        with self.ti:
            engine.plan(tasks, preferences)
        self.assertLess(self.ti.secs, self.max_time)


if __name__ == '__main__':
    unittest.main()

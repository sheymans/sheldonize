import sort
import unittest
import os
from timer import Timer

class TestSort(unittest.TestCase):
        
    def setUp(self):
        self.max_time = 0.5
        self.ti = Timer()

    def test_sort_tasks_20140623A(self):
        tasks = {2: {'due': 7}, 35L: {'duration': 12, 'comes_after': 36L, 'when': 0, 'due': 6}, 36L: {'when': 0, 'due': 4}}
        self.assertEqual(sort.sort_tasks(tasks), [36L, 35L, 2])

    def test_sort_tasks_20140624A(self):
        tasks = {45L: {'when': 0, 'due': 29}, 47L: {'when': 0, 'due': 5}}
        self.assertEqual(sort.sort_tasks(tasks), [47L, 45L])

    def test_sort_tasks_20140624B(self):
        tasks =  {45L: {'when': 0}, 47L: {'when': 0, 'due': 8}}
        self.assertEqual(sort.sort_tasks(tasks), [47L, 45L])

    def test_sort_tasks_20140624C(self):
        tasks = {1: {'when': 0 }, 2: {'when': 0, 'due': 5, 'comes_after': 1}, 3: {'when': 0}}
        # we want the unconstrainted stuff at the back not at the front
        self.assertEqual(sort.sort_tasks(tasks), [1, 2, 3])

    def test_smaller1(self):
        tasks = {1: {'when': 0 }, 2: {'when': 0, 'due': 5, 'comes_after': 1}, 3: {'when': 0}}
        self.assertEqual(sort.smaller_task_than(1, 2, tasks), 1)
        self.assertEqual(sort.smaller_task_than(1, 3, tasks), 0)

    def test_smaller2(self):
        tasks = {2: {'due': 7}, 35L: {'duration': 12, 'comes_after': 36L, 'when': 0, 'due': 6}, 36L: {'when': 0, 'due': 4}}
        self.assertEqual(sort.smaller_task_than(36L, 35L, tasks), -2)
        self.assertEqual(sort.smaller_task_than(36L, 2, tasks), -3)
        self.assertEqual(sort.smaller_task_than(35L, 2, tasks), -1)

    def test_smaller_with_priority1(self):
        tasks = {496L: {'priority': 3, 'when': 0}, 495L: {'priority': 1, 'when': 0, 'due': 27}}
        self.assertEqual(sort.smaller_task_than(495L, 496L, tasks), -2)

    def test_smaller_with_priority2(self):
        tasks = {496L: {'priority': 0, 'when': 0}, 495L: {'priority': 1, 'when': 0, 'due': 27}}
        self.assertEqual(sort.smaller_task_than(496L, 495L, tasks), -1)

    def test_smaller_with_priority3(self):
        tasks = {496L: {'priority': 0, 'when': 0}, 495L: {'priority': 1, 'when': 0}}
        self.assertEqual(sort.smaller_task_than(496L, 495L, tasks), -1)

    def test_smaller_with_priority4(self):
        tasks = {496L: {'when': 0}, 495L: {'priority': 3, 'when': 0}}
        self.assertEqual(sort.smaller_task_than(495L, 496L, tasks), -1)


    def test_sort_transitive_20140809(self):
        tasks = {145L: {'comes_after': 143L, 'when': 1}, 142L: {'comes_after': 145L, 'when': 1}, 143L: {'when': 1}}
        # we want to take care of comes_after as a transitive relation (this
        # requires a toposort)
        self.assertEqual(sort.sort_tasks(tasks), [143L, 145L, 142L])

    def test_sort_20140809B(self):
        tasks =  {'345': {'duration': 10, 'flex': 10, 'comes_after': '123', 'when': 1, 'due': 50}}
        sorted_tasks_ids =  ['345']
        # the sorted version should not contain ids if they are not present as
        # a key (but only in comes after)
        self.assertEqual(sort.sort_tasks(tasks), sorted_tasks_ids)


if __name__ == '__main__':
    unittest.main()

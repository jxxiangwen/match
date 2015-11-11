#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from match_algorithm_factory import MatchAlgorithmFactory
from plsa_algorithm import PlsaMatchAlgorithm
from lda_algorithm import LdaMatchAlgorithm
from cos_algorithm import CosMatchAlgorithm

__author__ = 'jxxia'


class TestMatchAlgorithmFactory(unittest.TestCase):
    def test_create_match_algorithm(self):
        match_algorithm_factory = MatchAlgorithmFactory()
        self.assertEqual(type(PlsaMatchAlgorithm()), type(match_algorithm_factory.create_match_algorithm('plsa')))
        self.assertEqual(type(LdaMatchAlgorithm()), type(match_algorithm_factory.create_match_algorithm('lda')))
        self.assertEqual(type(CosMatchAlgorithm()), type(match_algorithm_factory.create_match_algorithm('cos')))
        self.assertRaises(TypeError, match_algorithm_factory.create_match_algorithm, 'lsa')


if __name__ == '__main__':
    unittest.main()

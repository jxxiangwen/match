#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from cn.edu.shu.match.match_algorithm_factory import MatchAlgorithmFactory
from cn.edu.shu.match.lsi_algorithm import LsiMatchAlgorithm
from cn.edu.shu.match.lda_algorithm import LdaMatchAlgorithm
from cn.edu.shu.match.cos_algorithm import CosMatchAlgorithm

__author__ = 'jxxia'


class TestMatchAlgorithmFactory(unittest.TestCase):
    def test_create_match_algorithm(self):
        match_algorithm_factory = MatchAlgorithmFactory()
        self.assertEqual(type(LsiMatchAlgorithm()), type(match_algorithm_factory.create_match_algorithm('lsi')))
        self.assertEqual(type(LdaMatchAlgorithm()), type(match_algorithm_factory.create_match_algorithm('lda')))
        self.assertEqual(type(CosMatchAlgorithm()), type(match_algorithm_factory.create_match_algorithm('cos')))
        self.assertRaises(TypeError, match_algorithm_factory.create_match_algorithm, 'svm')


if __name__ == '__main__':
    unittest.main()

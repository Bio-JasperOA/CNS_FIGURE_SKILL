from __future__ import annotations
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from review_results import validate, packet, load_json


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.b=load_json(HERE/'examples/synthetic_multimodal.json')
    def codes(self,b=None,**kw):
        return {x['code'] for x in validate(b or self.b,**kw)['issues']}
    def test_valid_multimodal(self):
        r=validate(self.b,HERE/'examples',True)
        self.assertEqual(r['errors'],0);self.assertFalse(r['scientific_certification'])
        self.assertEqual(r['scientific_review'],'pending')
    def test_valid_benchmark(self):
        b=load_json(HERE/'examples/synthetic_benchmark.json')
        self.assertEqual(validate(b,HERE/'examples',True)['errors'],0)
    def test_validation_does_not_mutate(self):
        before=copy.deepcopy(self.b);validate(self.b);self.assertEqual(self.b,before)
    def test_duplicate_result(self):
        self.b['observations'].append(copy.deepcopy(self.b['observations'][0]));self.assertIn('DUPLICATE_ID',self.codes())
    def test_unknown_source(self):
        self.b['observations'][0]['source_refs']=['absent'];self.assertIn('UNKNOWN_SOURCE',self.codes())
    def test_unread_evidence(self):
        self.b['sources'][0]['read_scope']='not_read';self.assertIn('NO_READ_EVIDENCE',self.codes())
    def test_synthetic_mixing(self):
        self.b['sources'][0]['synthetic']=False;self.assertIn('SYNTHETIC_SCOPE',self.codes())
    def test_no_visual_statistics(self):
        self.b['observations'][0]['origin']='visual_only';self.assertIn('IMAGE_NUMBERS',self.codes())
    def test_image_only_source(self):
        self.b['sources'][0].update(kind='image',read_scope='image_only');self.assertIn('IMAGE_ONLY_STATS',self.codes())
    def test_nonfinite(self):
        self.b['observations'][0]['statistics']['estimate']=float('nan');self.assertIn('NONFINITE',self.codes())
    def test_ratio_null(self):
        self.b['observations'][0]['statistics']['scale']='ratio';self.assertIn('RATIO_SCALE',self.codes())
    def test_difference_null(self):
        self.b['observations'][0]['statistics']['null_value']=1;self.assertIn('NULL_SCALE',self.codes())
    def test_interval_order(self):
        self.b['observations'][0]['statistics']['ci'].update(lower=2,upper=1);self.assertIn('INTERVAL_ORDER',self.codes())
    def test_correlation_range(self):
        self.b['observations'][0]['statistics'].update(scale='correlation',estimate=2);self.assertIn('CORRELATION_RANGE',self.codes())
    def test_q_method(self):
        self.b['observations'][0]['statistics']['multiplicity']='unknown';self.assertIn('Q_WITHOUT_METHOD',self.codes())
    def test_invalid_probability(self):
        self.b['observations'][0]['statistics']['p_value']=-.1;self.assertIn('SCHEMA',self.codes())
    def test_sd_not_confidence(self):
        self.b['observations'][0]['statistics']['ci']['kind']='sd';self.assertIn('NOT_INFERENTIAL_INTERVAL',self.codes())
    def test_replicate_count(self):
        self.b['observations'][0]['design']['n_biological']['disease']=9000;self.assertIn('REPLICATE_COUNT',self.codes())
    def test_pseudoreplication(self):
        self.b['observations'][0]['design'].update(inferential_unit='cell',hierarchy_accounted=False);self.assertIn('PSEUDOREPLICATION',self.codes())
    def test_clustered_inference_permitted(self):
        self.b['observations'][0]['design'].update(inferential_unit='cell',hierarchy_accounted=True);self.assertNotIn('PSEUDOREPLICATION',self.codes())
    def test_pairing_mismatch(self):
        self.b['observations'][3]['design']['paired']=False;self.assertIn('PAIRING_MISMATCH',self.codes())
    def test_unknown_assay(self):
        self.b['observations'][0]['assay']='magic';self.assertIn('UNKNOWN_ASSAY',self.codes())
    def test_shared_data_warning(self):self.assertIn('SHARED_DATA',self.codes())
    def test_false_independent_methods(self):
        self.b['evidence_links'][0]['independence']='independent_specimens';self.assertIn('FALSE_INDEPENDENCE',self.codes())
    def test_false_independent_orthogonal_same_donors(self):
        self.b['evidence_links'][1]['independence']='independent_specimens';self.assertIn('FALSE_INDEPENDENCE',self.codes())
    def test_link_unknown(self):
        self.b['evidence_links'][0]['to']='missing';self.assertIn('LINK_ID',self.codes())
    def test_same_result_conflicting_roles(self):
        self.b['claims'][0]['contradicting_results']=['R1'];self.assertIn('CLAIM_ROLE_CONFLICT',self.codes())
    def test_supported_without_results(self):
        self.b['claims'][0]['supporting_results']=[];self.assertIn('UNSUPPORTED_CLAIM',self.codes())
    def test_failed_quality_support(self):
        self.b['observations'][0]['quality']['status']='failed';self.assertIn('FAILED_EVIDENCE',self.codes())
    def test_causal_escalation(self):
        self.b['claims'][0]['type']='causal';c=self.codes();self.assertIn('CAUSAL_DESIGN',c);self.assertIn('CAUSAL_EVIDENCE',c)
    def test_mechanism_inference_only(self):
        self.b['claims'][1]['type']='mechanistic';self.b['observations'][2]['origin']='inferred';self.assertIn('INFERENCE_ONLY_MECHANISM',self.codes())
    def test_equivalence_from_nonsignificance_rejected(self):
        c=self.b['claims'][3];c.update(type='equivalence',status='supported',supporting_results=['R5'],unresolved_results=[])
        self.assertIn('NONSIGNIFICANCE_NOT_EQUIVALENCE',self.codes())
    def test_equivalence_margin_conflict(self):
        self.b['observations'][4]['statistics']['equivalence']=dict(lower_margin=-.1,upper_margin=.1,method='CI-based declared test',margin_rationale='Synthetic teaching margin',decision='established')
        self.assertIn('EQUIVALENCE_CONFLICT',self.codes())
    def test_no_generalization_without_holdout(self):
        self.b['claims'][0]['type']='generalization';self.assertIn('NO_HOLDOUT',self.codes())
    def test_holdout_leakage(self):
        self.b['claims'][1]['type']='generalization'
        self.b['observations'][2]['design'].update(validation_role='independent_replication',validation_against='R1')
        self.assertIn('HOLDOUT_LEAKAGE',self.codes())
    def test_prediction_without_test(self):
        self.b['claims'][0]['type']='predictive';self.assertIn('PREDICTION_NO_TEST',self.codes())
    def test_hidden_result(self):
        self.b['claims'].pop();self.assertIn('UNACCOUNTED_RESULT',self.codes())
    def test_negative_result_exclusion(self):
        self.b['excluded_results']=[dict(result_id='R5',reason='not significant')];self.assertIn('SELECTIVE_REPORTING',self.codes())
    def test_unknown_narrative_id(self):
        self.b['narrative']['results_sections'][0]['result_ids']=['missing'];self.assertIn('NARRATIVE_RESULT',self.codes())
    def test_unknown_literature(self):
        self.b['narrative']['literature_refs']=['FakePaper'];self.assertIn('UNKNOWN_LITERATURE',self.codes())
    def test_cannot_automatically_accept(self):
        self.b['review']['status']='accepted';self.assertIn('SCHEMA',self.codes())
    def test_no_planned_result(self):
        self.b['observations'][0]['origin']='planned';self.assertIn('SCHEMA',self.codes())
    def test_local_source_missing(self):
        self.b['sources'][0]['path']='missing.csv';self.assertIn('MISSING_SOURCE',self.codes(root=HERE/'examples',verify_files=True))
    def test_path_traversal(self):
        self.b['sources'][0]['path']='../elsewhere.csv';self.assertIn('SOURCE_PATH',self.codes())
    def test_stale_hash(self):
        self.b['sources'][0]['sha256']='0'*64;self.assertIn('STALE_SOURCE',self.codes(root=HERE/'examples',verify_files=True))
    def test_numeric_binding_mismatch(self):
        self.b['observations'][0]['statistics']['estimate']=.5;self.assertIn('NUMERIC_BINDING',self.codes(root=HERE/'examples',verify_files=True))
    def test_duplicate_bound_row(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);s=(HERE/'examples/synthetic_results.csv').read_text();(root/'synthetic_results.csv').write_text(s+s.splitlines()[1]+'\n')
            self.b['sources'][0].pop('sha256');self.assertIn('NUMERIC_BINDING',self.codes(root=root,verify_files=True))
    def test_packet_labels_synthetic_and_pending(self):
        text=packet(self.b,validate(self.b));self.assertIn('SYNTHETIC TEACHING EXAMPLE',text);self.assertIn('not scientific acceptance',text)
    def test_cli_packet_and_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as t:
            cmd=[sys.executable,str(HERE/'review_results.py'),'packet',str(HERE/'examples/synthetic_multimodal.json'),'--root',str(HERE/'examples'),'--verify-files','--out',t]
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertTrue((Path(t)/'review_packet.md').exists())
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,2)
    def test_json_loader_rejects_nan(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{"x": NaN}')
            with self.assertRaises(ValueError):load_json(p)
    def test_source_symlink_escape(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'root';root.mkdir();outside=Path(t)/'outside.csv';outside.write_text('a\n1\n');(root/'synthetic_results.csv').symlink_to(outside)
            self.assertIn('MISSING_SOURCE',self.codes(root=root,verify_files=True))


if __name__=='__main__':unittest.main()

import argparse
import os
import random
from rdflib import Graph
import shutil
import subprocess
from tqdm import tqdm


def main(args):
    verbose = args.verbose
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    # Fetch all the input files
    input_files = [fn for fn in os.listdir(input_dir) if fn.endswith('.ttl')]
    
    # Generate data for each input file
    for input_f in tqdm(input_files):
        fn = '.'.join(input_f.split('.')[:-1])
        
        # Create output directory
        if not os.path.exists(os.path.join(output_dir, fn)):
            os.mkdir(os.path.join(output_dir, fn))

        graph = Graph()
        graph.parse(os.path.join(input_dir, input_f), format='turtle')
        
        # entity2id.txt
        entities = list(graph.subjects(predicate=None, object=None))
        entities.extend(list(graph.objects(subject=None, predicate=None)))
        unique_entities = list(set(entities))
        
        if verbose:
            print(f'Unique entities = {len(unique_entities)}')
    
        with open(os.path.join(output_dir, fn, 'entity2id.txt'), 'w') as relation_f:
            relation_f.write(str(len(unique_entities)) + '\n')
    
            for idx in range(len(unique_entities)):
                relation_f.write(f'{unique_entities[idx]}\t{idx}\n')
        
        # relation2id.txt
        relations = graph.predicates(subject=None, object=None)
        unique_relations = list(set(relations))

        if verbose:
            print(f'Unique relations = {len(unique_relations)}')
        
        with open(os.path.join(output_dir, fn, 'relation2id.txt'), 'w') as relation_f:
            relation_f.write(str(len(unique_relations)) + '\n')
    
            for idx in range(len(unique_relations)):
                relation_f.write(f'{unique_relations[idx]}\t{idx}\n')
                
        # triples (e1, e2, rel)
        triples = list(graph.triples((None, None, None)))

        if verbose:
            print(f'Triples = {len(triples)}')
    
        split_ratio = [0.8, 0.15, 0.05]  # [train, test, validation]
        slices = []

        start = 0
        for split in split_ratio:
            end = round(split * len(triples))
            slices.append((start, min(start + end, len(triples) - 1)))
            start += end
            
        if verbose:
            print(slices)

        validation = triples[slices[2][0]:slices[2][1]]

        train, test, validation = [triples[slice_[0]:slice_[1]] for slice_ in slices]
        
        if verbose:
            print(f'Train: {len(train)}\tTest: {len(test)}\tValidation: {len(validation)}')
        
        # train2id.txt
        with open(os.path.join(output_dir, fn, 'train2id.txt'), 'w') as train_f:
            train_f.write(str(len(train)) + '\n')
    
            for idx in range(len(train)):
                e1, rel, e2 = train[idx]
                e1_id = unique_entities.index(e1)
                e2_id = unique_entities.index(e2)
                rel_id = unique_relations.index(rel)

                train_f.write(f'{e1_id}\t{e2_id}\t{rel_id}\n')
                
        # test2id.txt
        with open(os.path.join(output_dir, fn, 'test2id.txt'), 'w') as test_f:
            test_f.write(str(len(test)) + '\n')
    
            for idx in range(len(test)):
                e1, rel, e2 = test[idx]
                e1_id = unique_entities.index(e1)
                e2_id = unique_entities.index(e2)
                rel_id = unique_relations.index(rel)

                test_f.write(f'{e1_id}\t{e2_id}\t{rel_id}\n')
        
        # valid2id.txt
        with open(os.path.join(output_dir, fn, 'valid2id.txt'), 'w') as validation_f:
            validation_f.write(str(len(validation)) + '\n')

            for idx in range(len(validation)):
                e1, rel, e2 = validation[idx]
                e1_id = unique_entities.index(e1)
                e2_id = unique_entities.index(e2)
                rel_id = unique_relations.index(rel)

                validation_f.write(f'{e1_id}\t{e2_id}\t{rel_id}\n')
                
        # Run n-n.py to generate extra files
        subprocess.Popen(['python3', '-m', 'n-n', '--input-dir', os.path.join(output_dir, fn)])

                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--input-dir', help='Directory containing the Turtle files')
    parser.add_argument('--output-dir', help='Directory for output files')
    parser.add_argument('-v', '--verbose', help='Verbosity', action='store_true')
    args = parser.parse_args()

    main(args)
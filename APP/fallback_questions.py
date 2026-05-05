"""Fallback questions when Gemini API is unavailable."""
import random

FALLBACK = {
  'math': {
    'Matrices': [
      {"question":"If A is a 2x2 matrix with |A|=5, what is |3A|?","correct":"45","incorrect1":"15","incorrect2":"9","incorrect3":"25","solution":"For nxn matrix, |kA| = k^n * |A|. So |3A| = 3^2 * 5 = 45."},
      {"question":"If A is a square matrix and A^2 = A, then A is called?","correct":"Idempotent","incorrect1":"Involutory","incorrect2":"Nilpotent","incorrect3":"Symmetric","solution":"A matrix A where A^2 = A is called idempotent."},
      {"question":"The transpose of a column matrix is?","correct":"Row matrix","incorrect1":"Column matrix","incorrect2":"Square matrix","incorrect3":"Diagonal matrix","solution":"Transposing a column matrix flips rows and columns, giving a row matrix."},
      {"question":"If A = [[1,2],[3,4]], what is trace of A?","correct":"5","incorrect1":"4","incorrect2":"10","incorrect3":"-2","solution":"Trace = sum of diagonal elements = 1 + 4 = 5."},
      {"question":"A matrix with all elements zero is called?","correct":"Null matrix","incorrect1":"Unit matrix","incorrect2":"Scalar matrix","incorrect3":"Identity matrix","solution":"A matrix with all elements equal to zero is called a null or zero matrix."},
      {"question":"If A is 3x2 and B is 2x4, order of AB is?","correct":"3x4","incorrect1":"2x2","incorrect2":"3x2","incorrect3":"2x4","solution":"AB has rows of A and columns of B: 3x4."},
      {"question":"Which matrix equals its transpose?","correct":"Symmetric matrix","incorrect1":"Skew-symmetric","incorrect2":"Diagonal","incorrect3":"Scalar","solution":"A symmetric matrix satisfies A = A^T."},
      {"question":"Determinant of a 2x2 identity matrix is?","correct":"1","incorrect1":"0","incorrect2":"2","incorrect3":"-1","solution":"det(I) = 1*1 - 0*0 = 1."},
      {"question":"If AB = BA, then A and B are?","correct":"Commutative","incorrect1":"Associative","incorrect2":"Distributive","incorrect3":"Inverse","solution":"When AB = BA, the matrices commute."},
      {"question":"Adjoint of a 2x2 matrix [[a,b],[c,d]] is?","correct":"[[d,-b],[-c,a]]","incorrect1":"[[a,-b],[-c,d]]","incorrect2":"[[d,b],[c,a]]","incorrect3":"[[d,c],[b,a]]","solution":"Swap diagonal, negate off-diagonal."},
    ],
    'Determinant': [
      {"question":"Determinant of [[2,3],[1,4]] is?","correct":"5","incorrect1":"11","incorrect2":"8","incorrect3":"-1","solution":"det = 2*4 - 3*1 = 8-3 = 5."},
      {"question":"If det(A)=0, then A is?","correct":"Singular","incorrect1":"Non-singular","incorrect2":"Orthogonal","incorrect3":"Unitary","solution":"A matrix with determinant 0 is singular (non-invertible)."},
      {"question":"det(kA) for 3x3 matrix A equals?","correct":"k^3 det(A)","incorrect1":"k det(A)","incorrect2":"k^2 det(A)","incorrect3":"3k det(A)","solution":"For nxn matrix, det(kA) = k^n * det(A). For 3x3: k^3 * det(A)."},
      {"question":"If two rows of a matrix are identical, its determinant is?","correct":"0","incorrect1":"1","incorrect2":"-1","incorrect3":"2","solution":"If two rows are identical, the determinant is always 0."},
      {"question":"det(A*B) equals?","correct":"det(A)*det(B)","incorrect1":"det(A)+det(B)","incorrect2":"det(A)-det(B)","incorrect3":"det(A)/det(B)","solution":"The determinant of a product equals the product of determinants."},
      {"question":"det(A^T) equals?","correct":"det(A)","incorrect1":"-det(A)","incorrect2":"1/det(A)","incorrect3":"det(A)^2","solution":"The determinant of a transpose equals the determinant of the original matrix."},
      {"question":"If det(A)=3, what is det(A^-1)?","correct":"1/3","incorrect1":"3","incorrect2":"-3","incorrect3":"0","solution":"det(A^-1) = 1/det(A) = 1/3."},
      {"question":"Interchanging two rows of a determinant?","correct":"Changes sign","incorrect1":"No change","incorrect2":"Doubles value","incorrect3":"Makes it zero","solution":"Swapping two rows multiplies the determinant by -1."},
      {"question":"Determinant of a diagonal matrix is?","correct":"Product of diagonal elements","incorrect1":"Sum of diagonal elements","incorrect2":"Always 1","incorrect3":"Always 0","solution":"For diagonal matrices, det = product of diagonal elements."},
      {"question":"Area of triangle with vertices using determinants gives?","correct":"Half the absolute determinant value","incorrect1":"The determinant value","incorrect2":"Double the determinant","incorrect3":"Square of determinant","solution":"Area = (1/2)|det| using the coordinate formula."},
    ],
  },
  'physics': {
    'Units and measurements': [
      {"question":"SI unit of force is?","correct":"Newton","incorrect1":"Joule","incorrect2":"Watt","incorrect3":"Pascal","solution":"Force = mass x acceleration. SI unit is Newton (kg.m/s^2)."},
      {"question":"1 light year is a unit of?","correct":"Distance","incorrect1":"Time","incorrect2":"Speed","incorrect3":"Intensity","solution":"A light year measures the distance light travels in one year."},
      {"question":"Dimensional formula of work is?","correct":"[ML^2T^-2]","incorrect1":"[MLT^-2]","incorrect2":"[ML^2T^-1]","incorrect3":"[MLT^-1]","solution":"Work = Force x Distance = [MLT^-2][L] = [ML^2T^-2]."},
      {"question":"Which is a derived unit?","correct":"Newton","incorrect1":"Kilogram","incorrect2":"Metre","incorrect3":"Second","solution":"Newton is derived from kg, m, and s. The others are base units."},
      {"question":"Number of base SI units is?","correct":"7","incorrect1":"5","incorrect2":"6","incorrect3":"9","solution":"The 7 base SI units are: m, kg, s, A, K, mol, cd."},
      {"question":"Dimensional formula of pressure is?","correct":"[ML^-1T^-2]","incorrect1":"[MLT^-2]","incorrect2":"[ML^2T^-2]","incorrect3":"[ML^-2T^-2]","solution":"Pressure = Force/Area = [MLT^-2]/[L^2] = [ML^-1T^-2]."},
      {"question":"1 fermi equals?","correct":"10^-15 m","incorrect1":"10^-10 m","incorrect2":"10^-12 m","incorrect3":"10^-9 m","solution":"1 fermi = 10^-15 metres, used for nuclear dimensions."},
      {"question":"Which quantity is dimensionless?","correct":"Strain","incorrect1":"Stress","incorrect2":"Force","incorrect3":"Pressure","solution":"Strain = change in length / original length, both in metres, so dimensionless."},
      {"question":"CGS unit of force is?","correct":"Dyne","incorrect1":"Newton","incorrect2":"Erg","incorrect3":"Poise","solution":"In CGS system, force is measured in dynes. 1 N = 10^5 dynes."},
      {"question":"Significant figures in 0.00520 are?","correct":"3","incorrect1":"5","incorrect2":"2","incorrect3":"4","solution":"Leading zeros don't count. 5, 2, and trailing 0 are significant = 3."},
    ],
  },
  'chemistry': {
    'Chemical reactions and equations': [
      {"question":"Balancing a chemical equation satisfies?","correct":"Law of conservation of mass","incorrect1":"Law of definite proportions","incorrect2":"Avogadro's law","incorrect3":"Dalton's law","solution":"Balanced equations ensure atoms are conserved (mass conservation)."},
      {"question":"In Fe2O3 + 3CO -> 2Fe + 3CO2, what is reduced?","correct":"Fe2O3","incorrect1":"CO","incorrect2":"Fe","incorrect3":"CO2","solution":"Fe2O3 loses oxygen (gains electrons) so it is reduced."},
      {"question":"Type of reaction: 2Mg + O2 -> 2MgO?","correct":"Combination","incorrect1":"Decomposition","incorrect2":"Displacement","incorrect3":"Double displacement","solution":"Two reactants combine to form one product = combination reaction."},
      {"question":"pH of a neutral solution is?","correct":"7","incorrect1":"0","incorrect2":"14","incorrect3":"1","solution":"A neutral solution has equal H+ and OH- ions, giving pH = 7."},
      {"question":"Rusting of iron is an example of?","correct":"Oxidation","incorrect1":"Reduction","incorrect2":"Neutralization","incorrect3":"Sublimation","solution":"Iron reacts with oxygen and moisture = oxidation (corrosion)."},
      {"question":"CaCO3 -> CaO + CO2 is what type?","correct":"Decomposition","incorrect1":"Combination","incorrect2":"Displacement","incorrect3":"Redox","solution":"One compound breaks into two products = decomposition."},
      {"question":"What is the product when acid reacts with base?","correct":"Salt and water","incorrect1":"Only salt","incorrect2":"Only water","incorrect3":"Gas","solution":"Acid + Base -> Salt + Water (neutralization)."},
      {"question":"Which gas is produced when zinc reacts with HCl?","correct":"Hydrogen","incorrect1":"Oxygen","incorrect2":"Chlorine","incorrect3":"Nitrogen","solution":"Zn + 2HCl -> ZnCl2 + H2. Hydrogen gas is evolved."},
      {"question":"Burning of magnesium ribbon is which type of reaction?","correct":"Exothermic","incorrect1":"Endothermic","incorrect2":"Reversible","incorrect3":"Neutral","solution":"Burning releases heat and light energy = exothermic."},
      {"question":"Number of atoms in 1 mole of any substance?","correct":"6.022 x 10^23","incorrect1":"6.022 x 10^22","incorrect2":"3.011 x 10^23","incorrect3":"6.022 x 10^24","solution":"Avogadro's number = 6.022 x 10^23 atoms/mole."},
    ],
  },
  'english': {
    'Grammar': [
      {"question":"Identify the noun: 'Honesty is the best policy.'","correct":"Honesty, policy","incorrect1":"is, best","incorrect2":"the, best","incorrect3":"is, the","solution":"Honesty (abstract noun) and policy (common noun) are nouns."},
      {"question":"Past tense of 'write' is?","correct":"Wrote","incorrect1":"Written","incorrect2":"Writed","incorrect3":"Writting","solution":"Write -> Wrote (past), Written (past participle)."},
      {"question":"Which is a conjunction?","correct":"But","incorrect1":"Quickly","incorrect2":"Beautiful","incorrect3":"Under","solution":"'But' connects two clauses; it is a conjunction."},
      {"question":"'She sings beautifully.' Identify the adverb.","correct":"Beautifully","incorrect1":"She","incorrect2":"Sings","incorrect3":"None","solution":"'Beautifully' modifies the verb 'sings', so it's an adverb."},
      {"question":"Plural of 'child' is?","correct":"Children","incorrect1":"Childs","incorrect2":"Childrens","incorrect3":"Childes","solution":"Child -> Children is an irregular plural."},
      {"question":"Which sentence is in passive voice?","correct":"The cake was eaten by her","incorrect1":"She ate the cake","incorrect2":"She is eating cake","incorrect3":"She eats cake","solution":"Object becomes subject + was/were + past participle = passive voice."},
      {"question":"'An' is used before words starting with?","correct":"Vowel sounds","incorrect1":"Consonants","incorrect2":"Any letter","incorrect3":"Only 'a'","solution":"'An' precedes words with vowel sounds: an apple, an hour."},
      {"question":"Superlative of 'good' is?","correct":"Best","incorrect1":"Better","incorrect2":"Goodest","incorrect3":"Most good","solution":"Good -> Better (comparative) -> Best (superlative). Irregular form."},
      {"question":"A pronoun replaces a?","correct":"Noun","incorrect1":"Verb","incorrect2":"Adjective","incorrect3":"Adverb","solution":"Pronouns (he, she, it, they) replace nouns to avoid repetition."},
      {"question":"Which is a preposition?","correct":"Between","incorrect1":"Slowly","incorrect2":"And","incorrect3":"Jump","solution":"'Between' shows relationship in space/position = preposition."},
    ],
  },
  'computer': {
    'Basics of Computer System': [
      {"question":"CPU stands for?","correct":"Central Processing Unit","incorrect1":"Central Program Unit","incorrect2":"Computer Personal Unit","incorrect3":"Central Peripheral Unit","solution":"CPU = Central Processing Unit, the brain of the computer."},
      {"question":"Which is an input device?","correct":"Keyboard","incorrect1":"Monitor","incorrect2":"Printer","incorrect3":"Speaker","solution":"Keyboard sends data INTO the computer = input device."},
      {"question":"1 KB equals?","correct":"1024 bytes","incorrect1":"1000 bytes","incorrect2":"512 bytes","incorrect3":"2048 bytes","solution":"1 KB = 2^10 = 1024 bytes."},
      {"question":"RAM stands for?","correct":"Random Access Memory","incorrect1":"Read Access Memory","incorrect2":"Random Automatic Memory","incorrect3":"Read Automatic Memory","solution":"RAM = Random Access Memory, volatile temporary storage."},
      {"question":"Which is an output device?","correct":"Printer","incorrect1":"Mouse","incorrect2":"Keyboard","incorrect3":"Scanner","solution":"Printer produces output from the computer."},
      {"question":"Binary number system has base?","correct":"2","incorrect1":"8","incorrect2":"10","incorrect3":"16","solution":"Binary uses only 0 and 1, so its base is 2."},
      {"question":"Which is volatile memory?","correct":"RAM","incorrect1":"ROM","incorrect2":"Hard Disk","incorrect3":"SSD","solution":"RAM loses data when power is off = volatile."},
      {"question":"Full form of ROM is?","correct":"Read Only Memory","incorrect1":"Random Only Memory","incorrect2":"Read Output Memory","incorrect3":"Run Only Memory","solution":"ROM = Read Only Memory, stores permanent instructions."},
      {"question":"ALU stands for?","correct":"Arithmetic Logic Unit","incorrect1":"Automatic Logic Unit","incorrect2":"Arithmetic Linear Unit","incorrect3":"Array Logic Unit","solution":"ALU performs arithmetic and logical operations inside CPU."},
      {"question":"Which generation used transistors?","correct":"Second","incorrect1":"First","incorrect2":"Third","incorrect3":"Fourth","solution":"1st=vacuum tubes, 2nd=transistors, 3rd=ICs, 4th=microprocessors."},
    ],
  },
  'environment': {
    'Ecosystem': [
      {"question":"Producers in an ecosystem are?","correct":"Green plants","incorrect1":"Herbivores","incorrect2":"Carnivores","incorrect3":"Decomposers","solution":"Green plants produce food via photosynthesis = producers."},
      {"question":"The term ecosystem was coined by?","correct":"A.G. Tansley","incorrect1":"Charles Darwin","incorrect2":"Gregor Mendel","incorrect3":"Ernst Haeckel","solution":"A.G. Tansley introduced the term 'ecosystem' in 1935."},
      {"question":"Which is a biotic component?","correct":"Plants","incorrect1":"Water","incorrect2":"Soil","incorrect3":"Sunlight","solution":"Biotic = living things. Plants are living organisms."},
      {"question":"Decomposers include?","correct":"Bacteria and fungi","incorrect1":"Lions and tigers","incorrect2":"Grass and trees","incorrect3":"Humans","solution":"Bacteria and fungi break down dead matter = decomposers."},
      {"question":"Energy flow in ecosystem is?","correct":"Unidirectional","incorrect1":"Bidirectional","incorrect2":"Multidirectional","incorrect3":"Circular","solution":"Energy flows one way: producers -> consumers -> decomposers."},
      {"question":"10% law of energy transfer was given by?","correct":"Lindeman","incorrect1":"Odum","incorrect2":"Tansley","incorrect3":"Elton","solution":"Lindeman's 10% law: only 10% energy transfers to next trophic level."},
      {"question":"Food web is formed by?","correct":"Interconnected food chains","incorrect1":"Single food chain","incorrect2":"Only producers","incorrect3":"Only consumers","solution":"Multiple interconnected food chains form a food web."},
      {"question":"Primary consumers are?","correct":"Herbivores","incorrect1":"Carnivores","incorrect2":"Omnivores","incorrect3":"Producers","solution":"Primary consumers eat plants directly = herbivores."},
      {"question":"Which is an abiotic factor?","correct":"Temperature","incorrect1":"Trees","incorrect2":"Animals","incorrect3":"Bacteria","solution":"Abiotic = non-living. Temperature is a non-living factor."},
      {"question":"Largest ecosystem on earth is?","correct":"Ocean","incorrect1":"Desert","incorrect2":"Forest","incorrect3":"Grassland","solution":"Oceans cover 71% of Earth's surface = largest ecosystem."},
    ],
  },
}

def get_fallback_questions(subject, topic, count=10):
    """Return fallback questions when AI is unavailable."""
    subj_data = FALLBACK.get(subject, {})
    topic_data = subj_data.get(topic, [])
    
    if not topic_data:
        # Try first available topic for this subject
        for t, qs in subj_data.items():
            if qs:
                topic_data = qs
                break
    
    if not topic_data:
        # Try any subject
        for s, topics in FALLBACK.items():
            for t, qs in topics.items():
                if qs:
                    topic_data = qs
                    break
            if topic_data:
                break
    
    selected = topic_data[:count] if len(topic_data) >= count else topic_data
    result = []
    for q in selected:
        result.append({
            'question': q['question'],
            'correct': q['correct'],
            'incorrect1': q['incorrect1'],
            'incorrect2': q['incorrect2'],
            'incorrect3': q['incorrect3'],
            'solution': q['solution'],
            'difficulty_level': random.choice(['Easy','Medium','Hard']),
            'topic_name': topic
        })
    return result

import java.io.File;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.SWRLRule;
import org.semanticweb.owlapi.util.DLExpressivityChecker;

public class CheckDL {
    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0] : "out/kb_v2_reasoned.owl";
        OWLOntologyManager man = OWLManager.createOWLOntologyManager();
        OWLOntology ont = man.loadOntologyFromOntologyDocument(new File(path));

        DLExpressivityChecker checker = new DLExpressivityChecker(Collections.singleton(ont));
        List<?> constructs = checker.getConstructs();
        Set<String> names = constructs.stream().map(Object::toString).collect(Collectors.toSet());

        boolean hasALC = names.contains("C") || (names.contains("U") && names.contains("E"));
        boolean hasTrans = names.contains("TRAN") || !ont.getAxioms(AxiomType.TRANSITIVE_OBJECT_PROPERTY).isEmpty();
        boolean hasR = names.contains("RRESTR") || names.contains("R") || !ont.getAxioms(AxiomType.SUB_PROPERTY_CHAIN_OF).isEmpty();
        boolean hasO = names.contains("O");
        boolean hasI = names.contains("I");
        boolean hasQ = names.contains("Q");
        boolean hasD = names.contains("(D)") || names.contains("D");

        StringBuilder compact = new StringBuilder();
        compact.append((hasALC && hasTrans) ? "S" : (hasALC ? "ALC" : ""));
        if (hasR) compact.append("R");
        if (hasO) compact.append("O");
        if (hasI) compact.append("I");
        if (hasQ) compact.append("Q");
        if (hasD) compact.append("(D)");

        System.out.println("==========================================");
        System.out.println("File              : " + path);
        System.out.println("DL Expressivity   : " + compact);
        System.out.println("OWLAPI Raw String : " + checker.getDescriptionLogicName());
        System.out.println("Constructs        : " + constructs);
        System.out.println("Classes           : " + ont.getClassesInSignature().size());
        System.out.println("Logical Axioms    : " + ont.getLogicalAxiomCount());
        Set<SWRLRule> rules = ont.getAxioms(AxiomType.SWRL_RULE);
        System.out.println("SWRL Rules        : " + rules.size());
        System.out.println("==========================================");
    }
}

package onlexnet.demo;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;
import org.springframework.modulith.docs.Documenter;

class ModularityTests {

    ApplicationModules modules = ApplicationModules.of(App.class);

    @Test
    void verifyModularity() {

        // Writing the application module arranagement to the console
        modules.forEach(System.out::println);

        // Trigger verification
        modules.verify();
    }

    // @Test
    void writeDocumentationSnippets() {

        new Documenter(modules)
                .writeModulesAsPlantUml()
                .writeIndividualModulesAsPlantUml();
    }
}

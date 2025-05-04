package onlexnet.webapi;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;

public class ApplicationModulesTest {

  @Test
  void createApplicationModuleModel() {
    var modules = ApplicationModules.of(WebapiApplication.class);
    modules.forEach(System.out::println);
  }
@Test
void verifyConfigurationClasses() {
    var modules = ApplicationModules.of(WebapiApplication.class);
    // Check if any module contains @Configuration classes
    modules.stream()
          .flatMap(module -> module.publicClasses().stream())
          .filter(clazz -> clazz.hasAnnotation("org.springframework.context.annotation.Configuration"))
          .forEach(System.out::println);
}

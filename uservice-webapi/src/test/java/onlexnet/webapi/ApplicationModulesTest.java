package onlexnet.webapi;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;

public class ApplicationModulesTest {

  @Test
  void createApplicationModuleModel() {
    var modules = ApplicationModules.of(WebapiApplication.class);
    modules.forEach(System.out::println);
  }
}

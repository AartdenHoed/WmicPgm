using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;


namespace ConfigMan.Extensions {


    public class TrimModelBinder : DefaultModelBinder {
        protected override void SetProperty(
            ControllerContext controllerContext,
            ModelBindingContext bindingContext,
            System.ComponentModel.PropertyDescriptor propertyDescriptor, object value) {
            if (propertyDescriptor.PropertyType == typeof(string)) {
                var val = (string)value;
                if (!string.IsNullOrEmpty(val))
                    val = value.ToString().Trim();

                value = val;
            }

            base.SetProperty(controllerContext, bindingContext,
                propertyDescriptor, value);
        }
    }
}
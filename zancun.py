    @allure.feature("邮件详情页")
    @allure.story("验证邮件删除逻辑")
    def test_email_delete_logic(self, driver):
        """验证邮件删除逻辑"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = 'src/resources/templates/common/gamehome/gamehome_button/gamehome_email_button_not_reddot_common.png'
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(template,threshold=first_found_threshold)
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(template,threshold=second_found_threshold)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=second_found_threshold)
                    attach_screenshot_to_allure(driver,'email_not_reddot_button_not_found','没有找到邮件按钮')
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}", "邮件钮查找结果", allure.attachment_type.TEXT)
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=first_found_threshold)
                    attach_screenshot_to_allure(driver,'email_button_found',"找到了邮件按钮")
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了邮件页"):
                        unread_template = 'src/resources/templates/common/email/email_button/email_select_unread_button_common.png'
                        first_found_threshold = 0.6
                        unread_result = image_matcher.find_template_in_screenshot(unread_template,first_found_threshold)
                        if not unread_result:
                            second_found_threshold = 0.45
                            unread_result = image_matcher.find_template_in_screenshot(unread_template,first_found_threshold)
                            image_matcher.create_marked_screenshot_for_single_template(template,threshold=second_found_threshold)
                            attach_screenshot_to_allure(driver,'email_select_unread_button_not_found','没有找到未读邮件按钮')
                        else:
                            unread_x, unread_y, unread_confidence = unread_result
                            unread_x, unread_y, unread_confidence = int(unread_x), int(unread_y), float(unread_confidence)
                            allure.attach(f"未读邮件按钮位置: ({unread_x}, {unread_y}), 置信度: {unread_confidence:.3f}", "未读邮件按钮查找结果", allure.attachment_type.TEXT)
                            image_matcher.create_marked_screenshot_for_single_template(unread_template,threshold=first_found_threshold)
                            attach_screenshot_to_allure(driver,'email_select_unread_button_found',"找到了未读邮件按钮")
                            
            except Exception as e:
                attach_screenshot_to_allure(driver, "email_button_click_error", f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}")
                pytest.exit(f"测试点击邮件按钮失败: {e}", returncode=1)

        with allure.step("点击已读邮件按钮进入已读列表"):
            try:
                image_matcher = create_image_matcher(driver)
                read_template = 'src/resources/templates/common/email/email_button/email_unselect_read_button_common.png'
                read_result = image_matcher.find_template_in_screenshot(read_template,threshold=0.6)
                first_found_threshold = 0.6
                if not read_result:
                    read_result = image_matcher.find_template_in_screenshot(read_template,first_found_threshold)
                    second_found_threshold = 0.45
                if not read_result:
                    image_matcher.create_marked_screenshot_for_single_template(read_template,second_found_threshold)
                    attach_screenshot_to_allure(driver,'email_select_read_button_not_found','没有找到已读邮件按钮')
                else:
                    read_x, read_y, read_confidence = read_result
                    read_x, read_y, read_confidence = int(read_x), int(read_y), float(read_confidence)
                    allure.attach(f"已读邮件按钮位置: ({read_x}, {read_y}), 置信度: {read_confidence:.3f}", "已读邮件按钮查找结果", allure.attachment_type.TEXT)
                    image_matcher.create_marked_screenshot_for_single_template(read_template,threshold=first_found_threshold)
                    attach_screenshot_to_allure(driver,'email_select_read_button_found',"找到了已读邮件按钮")
                    driver.click(read_x, read_y)
                    time.sleep(2)
                    
                    with allure.step("验证是否进入了已读列表"):
                        read_list_template = 'src/resources/templates/common/email/email_button/email_select_read_button_common.png'
                        first_found_threshold = 0.6
                        read_list_result = image_matcher.find_template_in_screenshot(read_list_template,first_found_threshold)
                        if not read_list_result:
                            second_found_threshold = 0.45
                            read_list_result = image_matcher.find_template_in_screenshot(read_list_template,first_found_threshold)
                            image_matcher.create_marked_screenshot_for_single_template(read_list_template,threshold=second_found_threshold)
                            attach_screenshot_to_allure(driver,'email_select_read_list_not_found','没有找到已读列表')
                        else:
                            read_list_x, read_list_y, read_list_confidence = read_list_result
                            read_list_x, read_list_y, read_list_confidence = int(read_list_x), int(read_list_y), float(read_list_confidence)
                            allure.attach(f"已读列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}", "已读列表查找结果", allure.attachment_type.TEXT)
                            image_matcher.create_marked_screenshot_for_single_template(read_list_template,threshold=first_found_threshold)
                            attach_screenshot_to_allure(driver,'email_select_read_list_found',"找到了已读列表")
                            
            except Exception as e:
                attach_screenshot_to_allure(driver, "email_unselect_read_button_click_error", f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}")
                pytest.exit(f"测试点击未读邮件按钮失败: {e}", returncode=1)

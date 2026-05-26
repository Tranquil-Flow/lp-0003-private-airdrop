#pragma once

#include <QWidget>

class IComponent {
public:
    virtual ~IComponent() = default;
    virtual QString id() const = 0;
    virtual QString displayName() const = 0;
    virtual QWidget* createWidget(QWidget* parent = nullptr) = 0;
};

#define IComponent_iid "org.logos.basecamp.IComponent/1.0"
Q_DECLARE_INTERFACE(IComponent, IComponent_iid)

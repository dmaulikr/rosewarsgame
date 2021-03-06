//
//  Position.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 2/13/13.
//
//

#import "GridLocation.h"

@implementation GridLocation

- (id)initWithRow:(NSUInteger)row column:(NSUInteger)column {
    
    self = [super init];
    
    if (self) {
        _row = row;
        _column = column;
    }
    
    return self;
}

+ (id)gridLocationWithRow:(NSUInteger)row column:(NSUInteger)column {
    
    return [[GridLocation alloc] initWithRow:row column:column];
}

- (id)copyWithZone:(NSZone *)zone {
    
    GridLocation *copyLocation = [[GridLocation allocWithZone:zone] init];
    
    copyLocation.row = self.row;
    copyLocation.column = self.column;
    
    return copyLocation;
}

- (NSUInteger)dictanceToGridLocation:(GridLocation*)gridLocation {
    
    return (NSUInteger)abs(gridLocation.column - self.column) + (NSUInteger)abs(gridLocation.row - self.row);
}

- (NSString *)description {
    
    return [NSString stringWithFormat:@"Row:%lu Column:%lu", (unsigned long)self.row, self.column];
}

- (NSUInteger)hash {
    
    return [[NSString stringWithFormat:@"%lu%lu", (unsigned long)self.row, (long)self.column] hash];
}

- (BOOL)isEqual:(id)object {
    
    if (![object isKindOfClass:[GridLocation class]]) {
        return NO;
    }
    
    GridLocation *location = object;
    
    BOOL isEqual = self.row == location.row &&
    self.column == location.column;
    
    return isEqual;
}

- (BOOL)isSameLocationAs:(GridLocation*)location {
    
    return [self isEqual:location];
}

- (BOOL)isInsideGameBoard {
    
    if (self.column >= 1 &&
        self.column <= BOARDSIZE_COLUMNS &&
        self.row >= 1 &&
        self.row <= BOARDSIZE_ROWS) {
        return YES;
    }
    
    return NO;
}

- (GridLocation*)locationAbove {
    
    return [GridLocation gridLocationWithRow:self.row - 1 column:self.column];
}

- (GridLocation*)locationBelow {
    
    return [GridLocation gridLocationWithRow:self.row + 1 column:self.column];
}

- (GridLocation *)locationToTheLeft {
    
    return [GridLocation gridLocationWithRow:self.row column:self.column - 1];
}

- (GridLocation *)locationToTheRight {
    
    return [GridLocation gridLocationWithRow:self.row column:self.column + 1];
}

- (NSArray*)perpendicularGridLocations {
    
    return @[[GridLocation gridLocationWithRow:self.row + 1 column:self.column + 1],
    [GridLocation gridLocationWithRow:self.row - 1 column:self.column - 1]];
}

- (NSArray *)surroundingGridLocations {
    
    return @[[self locationAbove],
    [self locationBelow],
    [self locationToTheLeft],
    [self locationToTheRight]];
}

- (NSArray*)surroundingEightGridLocations {
    
    return @[[GridLocation gridLocationWithRow:self.row column:self.column - 1],
             [GridLocation gridLocationWithRow:self.row - 1 column:self.column - 1],
             [GridLocation gridLocationWithRow:self.row column:self.column + 1],
             [GridLocation gridLocationWithRow:self.row + 1 column:self.column + 1],
             [GridLocation gridLocationWithRow:self.row - 1 column:self.column + 1],
             [GridLocation gridLocationWithRow:self.row - 1 column:self.column],
             [GridLocation gridLocationWithRow:self.row + 1 column:self.column - 1],
             [GridLocation gridLocationWithRow:self.row + 1 column:self.column]];
}

- (GridLocation *)getPushLocationForGridLocationWhenComingFromGridLocation:(GridLocation *)comingFromLocation {
    
    GridLocation *pushLocation;
    
    if ([comingFromLocation isSameLocationAs:[self locationAbove]]) {
        pushLocation = [self locationBelow];
    }
    
    if ([comingFromLocation isSameLocationAs:[self locationBelow]]) {
        pushLocation = [self locationAbove];
    }
    
    if ([comingFromLocation isSameLocationAs:[self locationToTheLeft]]) {
        pushLocation = [self locationToTheRight];
    }
    
    if ([comingFromLocation isSameLocationAs:[self locationToTheRight]]) {
        pushLocation = [self locationToTheLeft];
    }
    
    if ([pushLocation isInsideGameBoard]) {
        return pushLocation;
    }

    return nil;
}

- (GridLocation*)flipBacklineFromCurrentBackline:(NSUInteger)currentBackline {
    
    if (![self isInsideGameBoard]) return self;
    
    if (currentBackline == LOWER_BACKLINE) {
        self.row = (LOWER_BACKLINE - self.row) + UPPER_BACKLINE;
    }
    else {
        self.row = (UPPER_BACKLINE - self.row) + LOWER_BACKLINE;
    }
    
    return self;
}

@end
